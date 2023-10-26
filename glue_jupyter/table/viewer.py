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

from glue_jupyter.registries import viewer_registry

from ..view import IPyWidgetView


class TableState(ViewerState):
    hidden_components = ListCallbackProperty(docstring='Attributes to hide in the table display')


class TableBase(v.VuetifyTemplate):
    template_file = (__file__, 'table.vue')

    total_length = traitlets.CInt().tag(sync=True)
    checked = traitlets.List([]).tag(sync=True)  # indices of which rows are selected
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
        return {'descending': False, 'page': 1, 'itemsPerPage': 10,
                'sortBy': None, 'totalItems': len(self)}

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
        return [{'text': str(k), 'value': str(k), 'sortable': False} for k in components]

    def _get_items(self):
        if self.data is None:
            return []
        page = self.options['page'] - 1
        page_size = self.options['itemsPerPage']
        i1 = page * page_size
        i2 = min(len(self), (page + 1) * page_size)

        view = slice(i1, i2)
        masks = {}
        for k in self.data.subsets:
            try:
                masks[k.label] = k.to_mask(view)
            except IncompatibleAttribute:
                masks[k.label] = np.zeros(i2 - i1, dtype=bool)

        items = []
        for i in range(i2 - i1):
            item = {'__row__': i + i1}  # special key for the row number
            for selection in self.selections:
                selected = masks[selection][i]
                item[selection] = bool(selected)
            components = self.get_visible_components()
            for j, component in enumerate(components):
                item[str(component)] = self.format(self.data[component][i + i1])
            items.append(item)
        return items

    def vue_apply_filter(self, data):
        self.apply_filter()


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


class TableLayerStateWidget(widgets.VBox):
    def __init__(self, layer_state):
        super(TableLayerStateWidget, self).__init__()
        self.state = layer_state


class TableViewerStateWidget(widgets.VBox):
    def __init__(self, viewer_state):
        super(TableViewerStateWidget, self).__init__()
        self.state = viewer_state


@viewer_registry("table")
class TableViewer(IPyWidgetView):
    allow_duplicate_data = False
    allow_duplicate_subset = False

    _state_cls = TableState
    _options_cls = TableViewerStateWidget
    _data_artist_cls = TableLayerArtist
    _subset_artist_cls = TableLayerArtist
    _layer_style_widget_cls = TableLayerStateWidget

    tools = []

    def __init__(self, session, state=None):
        super(TableViewer, self).__init__(session, state=state)
        self.widget_table = TableGlue(data=None, apply_filter=self.apply_filter)
        self.create_layout()
        self.state.add_callback('hidden_components', self._update_hidden)

    def _update_hidden(self, *args):
        self.widget_table.hidden_components = self.state.hidden_components
        self.redraw()

    def redraw(self):
        subsets = [k.layer for k in self.layers if isinstance(k.layer, Subset)]
        with self.widget_table.hold_sync():
            self.widget_table.selections = [subset.label for subset in subsets]
            self.widget_table.selection_colors = [subset.style.color for subset in subsets]
        self.widget_table._update()

    def apply_filter(self):
        selected_rows = self.widget_table.checked
        subset_state = ElementSubsetState(indices=selected_rows, data=self.layers[0].layer)
        mode = self.session.edit_subset_mode
        mode.update(self._data, subset_state, focus_data=self.layers[0].layer)

    @property
    def figure_widget(self):
        return self.widget_table
