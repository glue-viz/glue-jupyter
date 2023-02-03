import os
import weakref

import ipywidgets as widgets
from IPython.display import display
import ipyvue

from glue.core.application_base import Application
from glue.core.link_helpers import LinkSame
from glue.core.roi import PolygonalROI
from glue.core.subset import RoiSubsetState
from glue.core.command import ApplySubsetState
from glue.core.edit_subset_mode import (NewMode, ReplaceMode, AndMode, OrMode,
                                        XorMode, AndNotMode)

from glue_jupyter.utils import _update_not_none, validate_data_argument
from glue_jupyter.widgets.subset_select_vuetify import SubsetSelect
from glue_jupyter.widgets.subset_mode_vuetify import SelectionModeMenu

from glue_jupyter.registries import viewer_registry

__all__ = ['JupyterApplication']

# TODO: move this to glue-core so that the subset mode can be set ot a string
# there too
SUBSET_MODES = {'new': NewMode, 'replace': ReplaceMode, 'and': AndMode,
                'or': OrMode, 'xor': XorMode, 'not': AndNotMode}

for name in ['glue-float-field', 'glue-throttled-slider']:
    file = f'{name.replace("-", "_")}.vue'
    ipyvue.register_component_from_file(
        None, name, os.path.join(os.path.dirname(__file__), 'widgets', file))


def is_bool(value):
    return isinstance(value, bool)


class JupyterApplication(Application):
    """
    The main Glue application object for the Jupyter environment.

    This is used as the primary way to interact with glue, including loading
    data, creating viewers, and adding links.

    Parameters
    ----------
    data_collection : `~glue.core.data_collection.DataCollection`
        A preexisting data collection. By default, a new data collection is
        created.
    session : `~glue.core.session.Session`
        A preexisting session object. By default, a new session object is
        created.
    settings : dict or None
        Initial settings to override defaults
    """

    def __init__(self, data_collection=None, session=None, settings=None):

        super(JupyterApplication, self).__init__(data_collection=data_collection, session=session)

        try:
            from glue.main import load_plugins
            load_plugins()
        except Exception:  # Compatibility with glue <0.16
            from glue.main import REQUIRED_PLUGINS
            REQUIRED_PLUGINS.clear()
            load_plugins()

        self._settings['new_subset_on_selection_tool_change'] = [False, bool]
        self._settings['single_global_active_tool'] = [True, bool]
        self._settings['disable_output_widget'] = [False, bool]

        if settings is not None:
            for key, value in settings.items():
                self.set_setting(key, value)

        self.output = None if self.get_setting('disable_output_widget') else widgets.Output()
        self.widget_data_collection = widgets.SelectMultiple()
        self.widget_subset_select = SubsetSelect(session=self.session)
        self.widget_subset_mode = SelectionModeMenu(session=self.session)

        if self.output is None:
            self.widget = widgets.VBox(children=[self.widget_subset_mode])
        else:
            self.widget = widgets.VBox(children=[self.widget_subset_mode, self.output])

        self._viewer_refs = []

    def _ipython_display_(self):
        display(self.widget)

    def link(self, links):
        """
        Parse and add links.
        """
        from glue.qglue import parse_links
        self.data_collection.add_link(parse_links(self.data_collection, links))

    def add_link(self, data1, attribute1, data2, attribute2):
        """
        Add a simple identity link between two attributes.

        Parameters
        ----------
        data1 : `~glue.core.data.Data`
            The dataset containing the first attribute.
        attribute1 : str or `~glue.core.component_id.ComponentID`
            The first attribute to link.
        data2 : `~glue.core.data.Data`
            The dataset containing the first attribute.
        attribute2 : str or `~glue.core.component_id.ComponentID`
            The first attribute to link.
        """
        # For now this assumes attribute1 and attribute2 are strings and single
        # attributes. In future we should generalize this while keeping the
        # simplest use case simple.
        att1 = data1.id[attribute1]
        att2 = data2.id[attribute2]
        link = LinkSame(att1, att2)
        self.data_collection.add_link(link)

    def set_subset_mode(self, mode):
        """
        Set the current subset mode.

        By default, selections in viewers update the current subset by
        replacing the previous selection with the new selection. However it is
        also possible to combine the current selection with previous selections
        using boolean operations.

        Parameters
        ----------
        mode : {'new', 'replace', 'and', 'or', 'xor', 'not'}
            The selection mode to use.
        """
        if mode in SUBSET_MODES:
            mode = SUBSET_MODES[mode]
        self.session.edit_subset_mode.mode = mode

    @property
    def viewers(self):
        """
        A list of viewers in this application - these are all viewers
        created that still have at least one reference to them even
        if not currently shown.
        """

        # Flush out viewers that are no longer referenced
        self._viewer_refs = [viewer for viewer in self._viewer_refs if viewer() is not None]

        # Now make a list of actual viewers rather than weakrefs, and flush out again
        # any unreferenced viewer
        viewers = [viewer() for viewer in self._viewer_refs]
        viewers = [viewer for viewer in viewers if viewer is not None]

        return viewers

    def new_data_viewer(self, *args, **kwargs):
        """
        Create a new data viewer

        This function can be called directly with the name of a viewer
        as the first parameter for any viewer types registered in the
        viewer_registry. Thus if a plug-in defines a viewer class as

        from glue_jupyter.registries import viewer_registry
        @viewer_registry("pluginviewer")
        class PluginViewer(Viewer):
            ...

        then this viewer can be created in a glue-jupyter app via:

        s = app.new_data_viewer('pluginviewer')

        This is the preferred way to call viewers defined in external plugins.
        """
        show = kwargs.pop('show', True)
        viewer_name = args[0]
        if isinstance(viewer_name, str):
            if viewer_name in viewer_registry.members:
                try:
                    viewer_cls = viewer_registry.members[viewer_name]['cls']
                except KeyError:
                    err_msg = "Registry does not define a Viewer class for {0}".format(viewer_name)
                    raise ValueError(err_msg)
            else:
                raise ValueError("No registered viewer found with name {0}".format(viewer_name))
            args = (viewer_cls, )
        viewer = super().new_data_viewer(*args, **kwargs)
        self._viewer_refs.append(weakref.ref(viewer))
        if show:
            viewer.show()
        return viewer

    def table(self, *, data=None, x=None, widget='ipyvuetify',  viewer_state=None,
              layer_state=None, show=True):
        """
        Open an interactive table viewer.

        Parameters
        ----------
        data : str or `~glue.core.data.Data`, optional
            The dataset to show in the viewer.
        widget : {'ipyvuetify', 'matplotlib'}
            Whether to use ipyvuetify or ... as table viewer
        viewer_state : `~glue.viewers.common.state.ViewerState`
            The initial state for the viewer (advanced).
        layer_state : `~glue.viewers.common.state.LayerState`
            The initial state for the data layer (advanced).
        show : bool, optional
            Whether to show the view immediately (`True`) or whether to only
            show it later if the ``show()`` method is called explicitly
            (`False`).
        """

        if widget == 'ipyvuetify':
            from .table import TableViewer
            viewer_cls = TableViewer
        else:
            raise ValueError("Widget type should be 'ipyvuetify'")

        data = validate_data_argument(self.data_collection, data)

        viewer_state_obj = viewer_cls._state_cls()
        viewer_state = viewer_state or {}

        viewer_state_obj.update_from_dict(viewer_state)

        view = self.new_data_viewer(viewer_cls, data=data,
                                    state=viewer_state_obj, show=show)
        layer_state = layer_state or {}
        view.layers[0].state.update_from_dict(layer_state)
        return view

    def histogram1d(self, *, data=None, x=None, widget='bqplot', color=None,
                    x_min=None, x_max=None, n_bin=None, normalize=False,
                    cumulative=False, viewer_state=None, layer_state=None,
                    show=True):
        """
        Open an interactive histogram viewer.

        Parameters
        ----------
        data : str or `~glue.core.data.Data`, optional
            The initial dataset to show in the viewer. Additional
            datasets can be added later using the ``add_data`` method on
            the viewer object.
        x : str or `~glue.core.component_id.ComponentID`, optional
            The attribute to show on the x axis.
        widget : {'bqplot', 'matplotlib'}
            Whether to use bqplot or Matplotlib as the front-end.
        color : str or tuple, optional
            The color to use for the data. Note that this will have the
            effect of setting the data color for all viewers.
        x_min : float, optional
            The lower value of the range to compute the histogram in.
        x_max : float, optional
            The upper value of the range to compute the histogram in.
        n_bin : int, optional
            The number of bins in the histogram.
        normalize : bool, optional
            Whether to normalize the histogram.
        cumulative : bool, optional
            Whether to show a cumulative histogram.
        viewer_state : `~glue.viewers.common.state.ViewerState`
            The initial state for the viewer (advanced).
        layer_state : `~glue.viewers.common.state.LayerState`
            The initial state for the data layer (advanced).
        show : bool, optional
            Whether to show the view immediately (`True`) or whether to only
            show it later if the ``show()`` method is called explicitly
            (`False`).
        """

        if widget == 'bqplot':
            from .bqplot.histogram import BqplotHistogramView
            viewer_cls = BqplotHistogramView
        elif widget == 'matplotlib':
            from .matplotlib.histogram import HistogramJupyterViewer
            viewer_cls = HistogramJupyterViewer
        else:
            raise ValueError("Widget type should be 'bqplot' or 'matplotlib'")

        data = validate_data_argument(self.data_collection, data)

        viewer_state_obj = viewer_cls._state_cls()
        viewer_state_obj.x_att_helper.append_data(data)
        viewer_state = viewer_state or {}

        if x is not None:
            viewer_state['x_att'] = data.id[x]

        # x_min and x_max get set to the hist_x_min/max in
        # glue.viewers.histogram.state for this API it make more sense to call
        # it x_min and x_max, and for consistency with the rest
        _update_not_none(viewer_state, hist_x_min=x_min, hist_x_max=x_max, hist_n_bin=n_bin,
                         normalize=normalize, cumulative=cumulative)
        viewer_state_obj.update_from_dict(viewer_state)

        view = self.new_data_viewer(viewer_cls, data=data,
                                    state=viewer_state_obj, show=show)
        layer_state = layer_state or {}
        _update_not_none(layer_state, color=color)
        view.layers[0].state.update_from_dict(layer_state)
        return view

    def scatter2d(self, *, data=None, x=None, y=None, widget='bqplot', color=None,
                  size=None, viewer_state=None, layer_state=None, show=True):
        """
        Open an interactive 2d scatter plot viewer.

        Parameters
        ----------
        data : str or `~glue.core.data.Data`, optional
            The initial dataset to show in the viewer. Additional
            datasets can be added later using the ``add_data`` method on
            the viewer object.
        x : str or `~glue.core.component_id.ComponentID`, optional
            The attribute to show on the x axis.
        y : str or `~glue.core.component_id.ComponentID`, optional
            The attribute to show on the y axis.
        widget : {'bqplot', 'matplotlib'}
            Whether to use bqplot or Matplotlib as the front-end.
        color : str or tuple, optional
            The color to use for the markers. Note that this will have the
            effect of setting the data color for all viewers.
        size : int or float
            The size to use for the markers. Note that this will have the
            effect of setting the marker size for all viewers.
        viewer_state : `~glue.viewers.common.state.ViewerState`
            The initial state for the viewer (advanced).
        layer_state : `~glue.viewers.common.state.LayerState`
            The initial state for the data layer (advanced).
        show : bool, optional
            Whether to show the view immediately (`True`) or whether to only
            show it later if the ``show()`` method is called explicitly
            (`False`).
        """

        if widget == 'bqplot':
            from .bqplot.scatter import BqplotScatterView
            viewer_cls = BqplotScatterView
        elif widget == 'matplotlib':
            from .matplotlib.scatter import ScatterJupyterViewer
            viewer_cls = ScatterJupyterViewer
        else:
            raise ValueError("Widget type should be 'bqplot' or 'matplotlib'")

        data = validate_data_argument(self.data_collection, data)

        viewer_state_obj = viewer_cls._state_cls()
        viewer_state_obj.x_att_helper.append_data(data)
        viewer_state_obj.y_att_helper.append_data(data)
        viewer_state = viewer_state or {}

        if x is not None:
            viewer_state['x_att'] = data.id[x]
        if y is not None:
            viewer_state['y_att'] = data.id[y]

        viewer_state_obj.update_from_dict(viewer_state)

        view = self.new_data_viewer(viewer_cls, data=data,
                                    state=viewer_state_obj, show=show)
        layer_state = layer_state or {}
        _update_not_none(layer_state, color=color, size=size)
        view.layers[0].state.update_from_dict(layer_state)
        return view

    def scatter3d(self, *, data=None, x=None, y=None, z=None, show=True):
        """
        Open an interactive 3d scatter plot viewer.

        Parameters
        ----------
        data : str or `~glue.core.data.Data`, optional
            The initial dataset to show in the viewer. Additional
            datasets can be added later using the ``add_data`` method on
            the viewer object.
        x : str or `~glue.core.component_id.ComponentID`, optional
            The attribute to show on the x axis.
        y : str or `~glue.core.component_id.ComponentID`, optional
            The attribute to show on the y axis.
        z : str or `~glue.core.component_id.ComponentID`, optional
            The attribute to show on the z axis.
        show : bool, optional
            Whether to show the view immediately (`True`) or whether to only
            show it later if the ``show()`` method is called explicitly
            (`False`).
        """

        from .ipyvolume import IpyvolumeScatterView

        data = validate_data_argument(self.data_collection, data)

        view = self.new_data_viewer(IpyvolumeScatterView, data=data, show=show)
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

    def imshow(self, *, data=None, x=None, y=None, widget='bqplot', show=True):
        """
        Open an interactive image viewer.

        Parameters
        ----------
        data : str or `~glue.core.data.Data`, optional
            The initial dataset to show in the viewer. Additional
            datasets can be added later using the ``add_data`` method on
            the viewer object.
        x : str or `~glue.core.component_id.ComponentID`, optional
            The attribute to show on the x axis. This should be one of the
            pixel axis attributes.
        y : str or `~glue.core.component_id.ComponentID`, optional
            The attribute to show on the y axis. This should be one of the
            pixel axis attributes.
        widget : {'bqplot', 'matplotlib'}
            Whether to use bqplot or Matplotlib as the front-end.
        show : bool, optional
            Whether to show the view immediately (`True`) or whether to only
            show it later if the ``show()`` method is called explicitly
            (`False`).
        """

        if widget == 'bqplot':
            from .bqplot.image import BqplotImageView
            viewer_cls = BqplotImageView
        elif widget == 'matplotlib':
            from .matplotlib.image import ImageJupyterViewer
            viewer_cls = ImageJupyterViewer
        else:
            raise ValueError("Widget type should be 'bqplot' or 'matplotlib'")

        data = validate_data_argument(self.data_collection, data)

        if len(data.pixel_component_ids) < 2:
            raise ValueError('Only data with two or more dimensions can be used '
                             'as the initial dataset in the image viewer')

        view = self.new_data_viewer(viewer_cls, data=data, show=show)

        if x is not None:
            x = data.id[x]
            view.state.x_att = x

        if y is not None:
            y = data.id[y]
            view.state.y_att = y

        return view

    def profile1d(self, *, data=None, x=None, widget='bqplot', show=True):
        """
        Open an interactive 1d profile viewer.

        Parameters
        ----------
        data : str or `~glue.core.data.Data`, optional
            The initial dataset to show in the viewer. Additional
            datasets can be added later using the ``add_data`` method on
            the viewer object.
        x : str or `~glue.core.component_id.ComponentID`, optional
            The attribute to show on the x axis. This should be a pixel or
            world coordinate `~glue.core.component_id.ComponentID`.
        widget : {'bqplot', 'matplotlib'}
            Whether to use bqplot or Matplotlib as the front-end.
        show : bool, optional
            Whether to show the view immediately (`True`) or whether to only
            show it later if the ``show()`` method is called explicitly
            (`False`).
        """

        if widget == 'bqplot':
            from .bqplot.profile import BqplotProfileView
            viewer_cls = BqplotProfileView
        elif widget == 'matplotlib':
            from .matplotlib.profile import ProfileJupyterViewer
            viewer_cls = ProfileJupyterViewer
        else:
            raise ValueError("Widget type should be 'matplotlib'")

        data = validate_data_argument(self.data_collection, data)

        view = self.new_data_viewer(viewer_cls, data=data, show=show)

        if x is not None:
            x = data.id[x]
            view.state.x_att = x

        return view

    def volshow(self, *, data=None, x=None, y=None, z=None, show=True):
        """
        Open an interactive volume viewer.

        Parameters
        ----------
        data : str or `~glue.core.data.Data`, optional
            The initial dataset to show in the viewer. Additional
            datasets can be added later using the ``add_data`` method on
            the viewer object.
        x : str or `~glue.core.component_id.ComponentID`, optional
            The attribute to show on the x axis. This should be one of the
            pixel axis attributes.
        y : str or `~glue.core.component_id.ComponentID`, optional
            The attribute to show on the y axis. This should be one of the
            pixel axis attributes.
        z : str or `~glue.core.component_id.ComponentID`, optional
            The attribute to show on the z axis. This should be one of the
            pixel axis attributes.
        show : bool, optional
            Whether to show the view immediately (`True`) or whether to only
            show it later if the ``show()`` method is called explicitly
            (`False`).
         """
        from .ipyvolume import IpyvolumeVolumeView

        data = validate_data_argument(self.data_collection, data)

        view = self.new_data_viewer(IpyvolumeVolumeView, data=data, show=show)

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

    def subset(self, name, subset_state):
        """
        Create a new selection/subset.

        Parameters
        ----------
        name : str
            The name of the new subset.
        subset_state : `~glue.core.subset.SubsetState`
            The definition of the subset. See the documentation at
            http://docs.glueviz.org/en/stable/python_guide/data_tutorial.html#defining-new-subsets
            for more information about creating subsets programmatically.
        """
        return self.data_collection.new_subset_group(name, subset_state)

    def subset_lasso2d(self, x_att, y_att, lasso_x, lasso_y):
        """
        Create a subset from a programmatic 2d lasso selection.

        Parameters
        ----------
        x_att : `~glue.core.component_id.ComponentID`
            The attribute corresponding to the x values being selected.
        y_att : `~glue.core.component_id.ComponentID`
            The attribute corresponding to the x values being selected.
        lasso_x : iterable
            The x values of the lasso.
        lasso_y : iterable
            The y values of the lasso.
        """
        roi = PolygonalROI(lasso_x, lasso_y)
        self.subset_roi([x_att, y_att], roi)

    def subset_roi(self, attributes, roi):
        """
        Create a subset from a region of interest.

        Parameters
        ----------
        attributes : iterable
            The attributes on the x and y axis
        roi : `~glue.core.roi.Roi`
            The region of interest to use to create the subset.
        """

        subset_state = RoiSubsetState(attributes[0], attributes[1], roi)
        cmd = ApplySubsetState(data_collection=self.data_collection,
                               subset_state=subset_state)
        self._session.command_stack.do(cmd)

    # Methods that we need to override to avoid the default behavior

    def _update_undo_redo_enabled(self, *args):
        pass  # TODO: if we want a gui for this, we need to update it here

    @staticmethod
    def _choose_merge(*args, **kwargs):
        # Never suggest automatic merging
        return None, None

    def add_widget(self, widget, label=None, tab=None):
        pass
