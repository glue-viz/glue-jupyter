import os
import numpy as np
import ipyvuetify as v
import ipywidgets as widgets
import traitlets
from echo import ListCallbackProperty
from glue.core.data import Subset
from glue.core.subset import ElementSubsetState
from glue.core.exceptions import IncompatibleAttribute
from glue.viewers.common.layer_artist import LayerArtist
from glue.viewers.common.state import ViewerState
from glue.viewers.common.tool import Tool
from glue.config import viewer_tool

from glue_jupyter import get_layout_factory
from glue_jupyter.registries import viewer_registry

from ..view import IPyWidgetView

ICONS_DIR = os.path.join(os.path.dirname(__file__), '..', 'icons')


class TableState(ViewerState):
    hidden_components = ListCallbackProperty(docstring='Attributes to hide in the table display')
    editable_components = ListCallbackProperty(docstring='Attributes that can be edited in the table')

    def is_editable(self, component_id):
        """Check if a component is editable using identity comparison."""
        for editable_cid in self.editable_components:
            if component_id is editable_cid:
                return True
        return False


class TableBase(v.VuetifyTemplate):
    template_file = (__file__, 'table.vue')

    total_length = traitlets.CInt().tag(sync=True)
    checked = traitlets.List([]).tag(sync=True)  # indices of which rows are selected
    all_selected = traitlets.Bool(False).tag(sync=True)
    items = traitlets.Any().tag(sync=True)  # the data, a list of dict
    headers = traitlets.Any().tag(sync=True)
    headers_selections = traitlets.Any().tag(sync=True)
    options = traitlets.Any().tag(sync=True)
    items_per_page = traitlets.CInt(11).tag(sync=True)
    selections = traitlets.Any([]).tag(sync=True)
    selection_colors = traitlets.Any([]).tag(sync=True)
    selection_enabled = traitlets.Bool(True).tag(sync=True)
    highlighted = traitlets.Int(None, allow_none=True).tag(sync=True)
    scrollable = traitlets.Bool(False).tag(sync=True)

    # for use with scrollable, when used in the default UI
    height = traitlets.Unicode(None, allow_none=True).tag(sync=True)

    hidden_components = traitlets.List([]).tag(sync=False)

    def _update(self):
        self._update_columns()
        self._update_items()
        self.total_length = len(self)
        self.options = {**self.options, 'totalItems': self.total_length}

    def _update_columns(self):
        self.headers = self._get_headers()

    @traitlets.observe('items_per_page')
    def _items_per_page(self, change):
        self._update_items()

    @traitlets.default('headers')
    def _headers(self):
        return self._get_headers()

    @traitlets.observe('selections')
    def _on_headers(self, change):
        self.headers_selections = self._get_headers_selections()

    @traitlets.default('headers_selections')
    def _headers_selections(self):
        return self._get_headers_selections()

    def _get_headers_selections(self):
        return [{'text': name, 'value': name, 'sortable': False} for name in self.selections]

    @traitlets.default('total_length')
    def _total_length(self):
        return len(self)

    @traitlets.default('options')
    def _options(self):
        return {'page': 1, 'itemsPerPage': 10,
                'sortBy': [], 'sortDesc': [], 'totalItems': len(self)}

    def format(self, value):
        return value

    def _update_items(self):
        self.items = self._get_items()

    @traitlets.default('items')
    def _items(self):
        return self._get_items()

    @traitlets.observe('options')
    def _on_change_options(self, change):
        self.items = self._get_items()

    def vue_apply_filter(self, data):
        pass

    def vue_select(self, data):
        is_checked, row = data['checked'], data['row']
        if not is_checked and row in self.checked:
            copy = self.checked[:]
            del copy[copy.index(row)]
            self.checked = copy
        if is_checked and row not in self.checked:
            self.checked = self.checked + [row]

    def vue_on_row_clicked(self, index):
        self.highlighted = index

    def vue_toggle_select_all(self, data):
        pass

    @traitlets.observe('checked')
    def _on_checked_change(self, change):
        self.all_selected = len(self) > 0 and len(change['new']) == len(self)

    def vue_sort_column(self, column):
        current_sort_by = self.options.get('sortBy', [])
        current_sort_desc = self.options.get('sortDesc', [])

        if current_sort_by and current_sort_by[0] == column:
            if not (current_sort_desc and current_sort_desc[0]):
                # Currently ascending, switch to descending
                new_options = {**self.options, 'sortBy': [column], 'sortDesc': [True]}
            else:
                # Currently descending, clear sort
                new_options = {**self.options, 'sortBy': [], 'sortDesc': []}
        else:
            # New column, sort ascending
            new_options = {**self.options, 'sortBy': [column], 'sortDesc': [False]}

        self.options = new_options

    def get_visible_components(self):
        components = []
        for cid in self.data.main_components + self.data.derived_components:
            # NOTE: we need to use a loop here instead of using 'not in' because
            # this doesn't work correctly with ComponentIDs (which override __eq__)
            for hidden_cid in self.hidden_components:
                if cid is hidden_cid:
                    break
            else:
                components.append(cid)
        return components


class TableGlue(TableBase):
    data = traitlets.Any()  # Glue data object
    apply_filter = traitlets.Any()  # callback
    state = traitlets.Any()  # TableState reference

    @traitlets.observe('data')
    def _on_data_change(self, change):
        self._update()

    def __len__(self):
        if self.data is None or len(self.data.shape) == 0:
            return 0
        return self.data.shape[0]

    def _get_headers(self):
        if self.data is None:
            return []
        components = self.get_visible_components()
        return [
            {
                'text': str(k),
                'value': str(k),
                'sortable': True,
                'editable': self.state is not None and self.state.is_editable(k)
            }
            for k in components
        ]

    def _get_sorted_indices(self):
        """Return indices that would sort the data by the current sort column."""
        sort_by = self.options.get('sortBy')
        if not sort_by:
            return np.arange(len(self))

        # sortBy can be a list (Vuetify 2.x) or a single value
        sort_column = sort_by[0] if isinstance(sort_by, list) else sort_by
        if not sort_column:
            return np.arange(len(self))

        # Find the component matching the sort column
        components = self.get_visible_components()
        component = None
        for c in components:
            if str(c) == sort_column:
                component = c
                break

        if component is None:
            return np.arange(len(self))

        values = self.data[component]
        indices = np.argsort(values)

        # Check for descending order
        sort_desc = self.options.get('sortDesc', self.options.get('descending', False))
        if isinstance(sort_desc, list):
            sort_desc = sort_desc[0] if sort_desc else False
        if sort_desc:
            indices = indices[::-1]

        return indices

    def _get_items(self):
        if self.data is None:
            return []
        page = self.options['page'] - 1
        page_size = self.options['itemsPerPage']
        i1 = page * page_size
        i2 = min(len(self), (page + 1) * page_size)

        # Get sorted indices and slice for current page
        sorted_indices = self._get_sorted_indices()
        page_indices = sorted_indices[i1:i2]

        masks = {}
        for k in self.data.subsets:
            try:
                full_mask = k.to_mask()
                masks[k.label] = full_mask[page_indices]
            except IncompatibleAttribute:
                masks[k.label] = np.zeros(len(page_indices), dtype=bool)

        items = []
        components = self.get_visible_components()
        for i, orig_idx in enumerate(page_indices):
            item = {'__row__': int(orig_idx)}  # original index for selections
            for selection in self.selections:
                selected = masks[selection][i]
                item[selection] = bool(selected)
            for component in components:
                item[str(component)] = self.format(self.data[component][orig_idx])
            items.append(item)
        return items

    def vue_apply_filter(self, data):
        self.apply_filter()

    def vue_toggle_select_all(self, data):
        if self.checked:
            self.checked = []
        else:
            self.checked = list(range(len(self)))

    def vue_cell_edited(self, data):
        """Handle cell edit from Vue frontend.

        Parameters
        ----------
        data : dict
            Dictionary with keys:
            - 'row': int, the row index (absolute, not page-relative)
            - 'column': str, the column/component name
            - 'value': any, the new value
        """
        row = data['row']
        column = data['column']
        new_value = data['value']

        # Find component ID
        component_id = None
        for cid in self.data.main_components + self.data.derived_components:
            if str(cid) == column:
                component_id = cid
                break

        if component_id is None:
            return

        # Update the data
        self._update_data_value(component_id, row, new_value)

    def _update_data_value(self, component_id, row_index, new_value):
        """Update value in glue Data object and notify linked viewers."""
        component = self.data.get_component(component_id)
        current_dtype = component.data.dtype

        # Type conversion
        try:
            if np.issubdtype(current_dtype, np.integer):
                converted_value = int(new_value)
            elif np.issubdtype(current_dtype, np.floating):
                converted_value = float(new_value)
            else:
                converted_value = new_value
        except (ValueError, TypeError):
            return  # Invalid input

        # Create updated array and use update_components
        new_data = component.data.copy()
        new_data[row_index] = converted_value
        self.data.update_components({component_id: new_data})

        # Refresh table
        self._update_items()


class TableLayerArtist(LayerArtist):
    def __init__(self, table_viewer, viewer_state, layer_state=None, layer=None):
        self._table_viewer = table_viewer
        super(TableLayerArtist, self).__init__(viewer_state, layer_state=layer_state, layer=layer)
        self._table_viewer.widget_table.data = layer.data

    def _refresh(self):
        self._table_viewer.redraw()

    def redraw(self):
        self._refresh()

    def update(self):
        self._refresh()

    def clear(self):
        self._refresh()

    def remove(self):
        data = None
        if self._table_viewer.layers:
            last_layer = self._table_viewer.layers[-1]
            data = last_layer.layer.data
        self._table_viewer.widget_table.data = data
        self._refresh()


class TableLayerStateWidget(widgets.VBox):
    def __init__(self, layer_state):
        super(TableLayerStateWidget, self).__init__()
        self.state = layer_state


class TableViewerStateWidget(v.VuetifyTemplate):
    template_file = (__file__, 'viewer_state.vue')

    column_items = traitlets.List([]).tag(sync=True)
    visible_columns = traitlets.List([]).tag(sync=True)

    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer
        self.state = viewer.state
        self._updating = False

        # Sync from state to widget
        self.state.add_callback('hidden_components', self._on_hidden_changed)

    def update_columns(self, data):
        """Update available columns when data changes."""
        if data is None:
            self.column_items = []
            self.visible_columns = []
            return

        all_components = data.main_components + data.derived_components
        self.column_items = [{'text': str(c), 'value': str(c)} for c in all_components]

        # Set visible columns (all minus hidden)
        hidden_names = [str(c) for c in self.state.hidden_components]
        self.visible_columns = [str(c) for c in all_components if str(c) not in hidden_names]

    def _on_hidden_changed(self, *args):
        """Sync from state.hidden_components to widget."""
        if self._updating:
            return
        data = self.viewer.widget_table.data
        if data is None:
            return
        all_components = data.main_components + data.derived_components
        hidden_names = [str(c) for c in self.state.hidden_components]
        self.visible_columns = [str(c) for c in all_components if str(c) not in hidden_names]

    @traitlets.observe('visible_columns')
    def _on_visible_changed(self, change):
        """Sync from widget to state.hidden_components."""
        data = self.viewer.widget_table.data
        if data is None:
            return

        self._updating = True
        try:
            all_components = data.main_components + data.derived_components
            visible_names = set(change['new'])
            hidden = [c for c in all_components if str(c) not in visible_names]
            self.state.hidden_components = hidden
        finally:
            self._updating = False


@viewer_tool
class TableApplySubset(Tool):

    icon = os.path.join(ICONS_DIR, 'row_select.svg')
    tool_id = 'table:apply_subset'
    action_text = 'Apply subset from selection'
    tool_tip = 'Create a subset from the selected rows'

    def __init__(self, viewer):
        self.viewer = viewer

    def activate(self):
        self.viewer.apply_filter()


@viewer_registry("table")
class TableViewer(IPyWidgetView):
    allow_duplicate_data = False
    allow_duplicate_subset = False

    _state_cls = TableState
    _options_cls = TableViewerStateWidget
    _data_artist_cls = TableLayerArtist
    _subset_artist_cls = TableLayerArtist
    _layer_style_widget_cls = TableLayerStateWidget

    tools = ['table:apply_subset']

    def __init__(self, session, state=None):
        super(TableViewer, self).__init__(session, state=state)
        self.widget_table = TableGlue(data=None, apply_filter=self.apply_filter, state=self.state)
        self.create_layout()
        self.state.add_callback('hidden_components', self._update_hidden)
        self.state.add_callback('editable_components', self._update_editable)

    def create_layout(self):
        # Override to pass viewer instead of just state
        self._layout_viewer_options = self._options_cls(self)

        layout_factory = get_layout_factory()
        if layout_factory is None:
            raise ValueError('layout factory should be set with set_layout_factory')
        else:
            self._layout = layout_factory(self)

    def _update_hidden(self, *args):
        self.widget_table.hidden_components = self.state.hidden_components
        self.redraw()

    def _update_editable(self, *args):
        self.widget_table._update_columns()

    def redraw(self):
        subsets = [k.layer for k in self.layers if isinstance(k.layer, Subset)]
        with self.widget_table.hold_sync():
            self.widget_table.selections = [subset.label for subset in subsets]
            self.widget_table.selection_colors = [subset.style.color for subset in subsets]
        self.widget_table._update()
        self._layout_viewer_options.update_columns(self.widget_table.data)

    def apply_filter(self):
        selected_rows = self.widget_table.checked
        subset_state = ElementSubsetState(indices=selected_rows, data=self.layers[0].layer)
        mode = self.session.edit_subset_mode
        mode.update(self._data, subset_state, focus_data=self.layers[0].layer)

    @property
    def figure_widget(self):
        return self.widget_table
