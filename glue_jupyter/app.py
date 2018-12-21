import ipywidgets as widgets
import ipymaterialui as mui
from IPython.display import display


from glue.core.application_base import Application
from glue.core import message as msg
from glue.core.link_helpers import LinkSame
from glue.core.roi import PolygonalROI, CircularROI, RectangularROI, Projected3dROI
from glue.core.subset import RoiSubsetState3d, RoiSubsetState
from glue.core.command import ApplySubsetState
from glue.core.edit_subset_mode import (EditSubsetMode, OrMode, AndNotMode,
                                        AndMode, XorMode, ReplaceMode)

import glue.icons

from glue_jupyter.utils import _update_not_none
from glue_jupyter.widgets.subset_select import SubsetSelect
from glue_jupyter.widgets.subset_mode import SubsetMode


# not sure we need to inherit: from glue.core.application_base import Application
# what would we gain that would be natural in the notebook?
class JupyterApplication(Application):

    def __init__(self, data_collection=None, session=None):
        super(JupyterApplication, self).__init__(data_collection=data_collection, session=session)
        self.output = widgets.Output()
        self.widget_data_collection = widgets.SelectMultiple()
        self.widget_subset_select = SubsetSelect(self.session)
        self.widget_subset_mode = SubsetMode(self.session)
        self.widget = widgets.VBox(children=[self.widget_subset_mode, self.output])

    def _ipython_display_(self):
        display(self.widget)

    def link(self, links):
        from glue.qglue import parse_links
        self.data_collection.add_link(parse_links(self.data_collection, links))

    def add_link(self, data1, attribute1, data2, attribute2, function=None):
        # For now this assumes attribute1 and attribute2 are strings and single
        # attributes. In future we should generalize this while keeping the
        # simplest use case simple.
        if function is not None:
            raise NotImplementedError
        att1 = data1.id[attribute1]
        att2 = data2.id[attribute2]
        link = LinkSame(att1, att2)
        self.data_collection.add_link(link)

    def subset_mode(self, mode):
        self.session.edit_subset_mode.mode = mode

    def subset_mode_replace(self):
        self.subset_mode(ReplaceMode)

    def subset_mode_and(self):
        self.subset_mode(AndMode)

    def subset_lasso2d(self, x, y, xvalues, yvalues):
        roi = PolygonalROI(xvalues, yvalues)
        self.subset_roi([x, y], roi)

    def subset_roi(self, components, roi, use_current=False):
        subset_state = RoiSubsetState(components[0], components[1], roi)
        cmd = ApplySubsetState(data_collection=self.data_collection,
                               subset_state=subset_state,
                               use_current=use_current)
        self._session.command_stack.do(cmd)

    def _roi_to_subset_state(self, components, roi):
        return RoiSubsetState(components[0], components[1], roi)

    def add_widget(self, widget, label=None, tab=None):
        pass

    # TODO: remove when https://github.com/glue-viz/glue/pull/1877 is merged
    def new_data_viewer(self, viewer_class, data=None, state=None):
        """
        Create a new data viewer, add it to the UI,
        and populate with data

        """
        from glue.core import BaseData

        if viewer_class is None:
            return

        if state is not None:
            c = viewer_class(self._session, state=state)
        else:
            c = viewer_class(self._session)
        c.register_to_hub(self._session.hub)

        if data is not None:
            if isinstance(data, BaseData):
                result = c.add_data(data)
            elif isinstance(data, Subset):
                result = c.add_subset(data)
            if not result:
                c.close(warn=False)
                return

        self.add_widget(c)
        c.show()
        return c


    def histogram1d(self, x=None, data=None, widget='bqplot', color=None, x_min=None, x_max=None, hist_n_bin=None, normalize=False, cumulative=False, viewer_state=None, layer_state=None):
        if widget == 'bqplot':
            from .bqplot import BqplotHistogramView
            viewer_cls = BqplotHistogramView
        elif widget == 'matplotlib':
            from .matplotlib.histogram import HistogramJupyterViewer
            viewer_cls = HistogramJupyterViewer
        else:
            raise ValueError("Widget type should be 'bqplot' or 'matplotlib'")
        if data is None and len(self._data) != 1:
            raise ValueError('There is more than 1 data set in the data collection, please pass a data argument')
        data = data or self._data[0]

        state = viewer_cls._state_cls()
        state.x_att_helper.append_data(data)

        viewer_state_obj = viewer_cls._state_cls()
        viewer_state_obj.x_att_helper.append_data(data)
        viewer_state = viewer_state or {}
        if x is not None:
            viewer_state['x_att'] = data.id[x]
        # x_min and x_max get set to the hist_x_min/max in glue.viewers.histogram.state
        # for this API it make more sense to call it x_min and x_max, and for consistency with the rest
        _update_not_none(viewer_state, hist_x_min=x_min, hist_x_max=x_max, hist_n_bin=hist_n_bin,
            normalize=normalize, cumulative=cumulative)
        viewer_state_obj.update_from_dict(viewer_state)

        view = self.new_data_viewer(viewer_cls, data=data, state=viewer_state_obj)
        layer_state = layer_state or {}
        _update_not_none(layer_state, color=color)
        view.layers[0].state.update_from_dict(layer_state)
        return view

    def scatter2d(self, x=None, y=None, data=None, widget='bqplot', color=None, size=None, viewer_state=None, layer_state=None):
        if widget == 'bqplot':
            from .bqplot import BqplotScatterView
            viewer_cls = BqplotScatterView
        elif widget == 'matplotlib':
            from .matplotlib.scatter import ScatterJupyterViewer
            viewer_cls = ScatterJupyterViewer
        else:
            raise ValueError("Widget type should be 'bqplot' or 'matplotlib'")
        if data is None and len(self._data) != 1:
            raise ValueError('There is more than 1 data set in the data collection, please pass a data argument')
        data = data or self._data[0]
        viewer_state_obj = viewer_cls._state_cls()
        viewer_state_obj.x_att_helper.append_data(data)
        viewer_state_obj.y_att_helper.append_data(data)
        viewer_state = viewer_state or {}
        if x is not None:
            viewer_state['x_att'] = data.id[x]
        if x is not None:
            viewer_state['y_att'] = data.id[y]
        viewer_state_obj.update_from_dict(viewer_state)

        view = self.new_data_viewer(viewer_cls, data=data, state=viewer_state_obj)
        layer_state = layer_state or {}
        _update_not_none(layer_state, color=color, size=size)
        view.layers[0].state.update_from_dict(layer_state)
        return view

    def scatter3d(self, x=None, y=None, z=None, data=None):
        from .ipyvolume import IpyvolumeScatterView
        if data is None and len(self._data) != 1:
            raise ValueError('There is more than 1 data set in the data collection, please pass a data argument')
        data = data or self._data[0]
        view = self.new_data_viewer(IpyvolumeScatterView, data=data)
        if x is not None:
            x = data.id[x]
            view.state.x_att = x
        if y is not None:
            y = data.id[y]
            view.state.y_att = y
        if z is not None:
            z = data.id[z]
            view.state.z_att = z
        return view

    def imshow(self, x=None, y=None, data=None, widget='bqplot'):
        if widget == 'bqplot':
            from .bqplot import BqplotImageView
            viewer_cls = BqplotImageView
        elif widget == 'matplotlib':
            from .matplotlib.image import ImageJupyterViewer
            viewer_cls = ImageJupyterViewer
        else:
            raise ValueError("Widget type should be 'bqplot' or 'matplotlib'")
        data = data or self._data[0]
        if data is None and len(self._data) != 1:
            raise ValueError('There is more than 1 data set in the data collection, please pass a data argument')
        if len(data.pixel_component_ids) < 2:
            raise ValueError('There are less than 2 pixel components (not an image?)')
        view = self.new_data_viewer(viewer_cls, data=data)
        if x is not None:
            x = data.id[x]
            view.state.x_att = x
        if y is not None:
            y = data.id[y]
            view.state.y_att = y
        return view

    def profile1d(self, x, data=None, widget='matplotlib'):
        if widget == 'matplotlib':
            from .matplotlib.profile import ProfileJupyterViewer
            viewer_cls = ProfileJupyterViewer
        else:
            raise ValueError("Widget type should be 'matplotlib'")
        data = data or self._data[0]
        view = self.new_data_viewer(viewer_cls, data=data)
        if x is not None:
            x = data.id[x]
            view.state.x_att = x
        return view

    def volshow(self, x="Pixel Axis 2 [x]", y="Pixel Axis 1 [y]", z="Pixel Axis 0 [z]", data=None):
        from .ipyvolume import IpyvolumeVolumeView
        data = data or self._data[0]
        if data is None and len(self._data) != 1:
            raise ValueError('There is more than 1 data set in the data collection, please pass a data argument')
        view = self.new_data_viewer(IpyvolumeVolumeView, data=data)
        if x is not None:
            x = data.id[x]
            view.state.x_att = x
        if y is not None:
            y = data.id[y]
            view.state.y_att = y
        if z is not None:
            z = data.id[z]
            view.state.z_att = z
        return view

    def subset(self, name, state):
        return self.data_collection.new_subset_group(name, state)

    def _update_undo_redo_enabled(self, *args):
        pass  # TODO: if we want a gui for this, we need to update it here

    @staticmethod
    def _choose_merge(*args, **kwargs):
        # Never suggest automatic merging
        return None, None
