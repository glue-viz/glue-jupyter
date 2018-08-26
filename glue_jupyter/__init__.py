from __future__ import absolute_import
from glue.core import message as msg
from glue.core.subset import Subset
from glue.viewers.common.viewer import Viewer
from glue.core.layer_artist import LayerArtistContainer
from glue.core.edit_subset_mode import (EditSubsetMode, OrMode, AndNotMode,
                                        AndMode, XorMode, ReplaceMode)
from glue.core.roi import PolygonalROI, CircularROI, RectangularROI, Projected3dROI
from glue.core.subset import RoiSubsetState3d, RoiSubsetState
from glue.core.command import ApplySubsetState
from IPython.display import display
import ipywidgets as widgets
import six
# from glue.core.session import Session
# from glue.viewers.scatter.layer_artist import ScatterLayerArtist


def load(path):
    from glue.core.data_factories import load_data
    return load_data(path)

def jglue(*args, **kwargs):
    from glue.core import DataCollection
    from glue.app.qt import GlueApplication
    from glue.qglue import parse_data, parse_links
    from glue.core.data_factories import load_data

    links = kwargs.pop('links', None)

    dc = DataCollection()
    for label, data in kwargs.items():
        if isinstance(data, six.string_types):
            data = load_data(data)
        dc.extend(parse_data(data, label))
    for data in args:
        dc.append(data)

    if links is not None:
        dc.add_link(parse_links(dc, links))

    japp = JupyterApplication(dc)
    return japp

def example_data_xyz(seed=42, N=500, loc=0, scale=1):
    from glue.core import Data
    import numpy as np
    rng = np.random.RandomState(seed)
    x, y, z = rng.normal(loc, scale, size=(3, N))
    vx = x - x.mean()
    vy = y - y.mean()
    vz = z - z.mean()
    speed = np.sqrt(vx**2 + vy**2 + vz**2)
    data_xyz = Data(x=x, y=y, z=z, vx=vx, vy=vy, vz=vz, speed=speed, label="xyz data")
    return data_xyz

def example_volume(shape=64, limits=[-4, 4]):
    """Creates a test data set containing a ball"""
    from glue.core import Data
    import numpy as np
    import ipyvolume as ipv
    ball_data = ipv.examples.ball(shape=shape, limits=limits, show=False, draw=False)
    data = Data()
    data.add_component(ball_data, label='intensity')
    return data

def example_image(shape=64, limits=[-4, 4]):
    """Creates a test data set containing a ball"""
    from glue.core import Data, Coordinates
    import numpy as np
    import ipyvolume as ipv
    x = np.linspace(-3, 3, num=shape)
    X, Y = np.meshgrid(x, x)
    rho = 0.8
    I = np.exp(-X**2-Y**2-2*X*Y*rho)
    data = Data()
    data.coords = Coordinates()
    data.add_component(I, label='intensity')
    return data

# not sure we need to inherit: from glue.core.application_base import Application
# what would we gain that would be natural in the notebook?
from glue.core.application_base import Application

class JupyterApplication(Application):

    def __init__(self, data_collection=None, session=None):
        super(JupyterApplication, self).__init__(data_collection=data_collection, session=session)
        self.selection_modes = [('replace', ReplaceMode), ('add', OrMode), ('and', AndMode), ('xor', XorMode), ('remove', AndNotMode)]
        self.widget_selection_mode = widgets.ToggleButtons(
            options=[label for label, mode in self.selection_modes],
            description='Selection mode:',
            disabled=False,
            tooltips=[label for label, mode in self.selection_modes],
        )
        self.widget_data_collection = widgets.SelectMultiple()
        self.widget_subset_groups   = widgets.SelectMultiple()
        self.widget = widgets.VBox(children=[self.widget_selection_mode, self.widget_subset_groups])
        self.widget_selection_mode.observe(self._set_selection_mode, 'index')
        self.widget_subset_groups.observe(self._set_subset_groups, 'index')
        self.session.hub.subscribe(self, msg.EditSubsetMessage, handler=self._on_edit_subset_msg)
        self.session.hub.subscribe(self, msg.SubsetCreateMessage, handler=self._on_subset_create_msg)
        self._update_subset_mode(self.session.edit_subset_mode.mode)
        self._update_subset_groups_selected(self.session.edit_subset_mode.edit_subset)
        display(self.widget)

    def link(self, links):
        from glue.qglue import parse_links
        self.data_collection.add_link(parse_links(self.data_collection, links))

    def _on_edit_subset_msg(self, msg):
        self._update_subset_mode(msg.mode)
        self._update_subset_groups_selected(msg.subset)

    def _on_subset_create_msg(self, msg):
        self._update_subset_groups_selected(self.session.edit_subset_mode.edit_subset)

    def _update_subset_mode(self, mode):
        if self.session.edit_subset_mode.mode != mode:
            self.session.edit_subset_mode.mode = mode
        index = 0
        EditSubsetMode
        for i, (name, sel_mode) in enumerate(self.selection_modes):
            if mode == sel_mode:
                index = i
        self.widget_selection_mode.index = index

    def _update_subset_groups_selected(self, subset_groups_selected):
        if self.session.edit_subset_mode.edit_subset != subset_groups_selected:
            self.session.edit_subset_mode.edit_subset = subset_groups_selected
        options = []
        indices = []
        for i, subset_group in enumerate(self.data_collection.subset_groups):
            options.append(subset_group.label)
            if subset_group in self.session.edit_subset_mode.edit_subset:
                indices.append(i)
        self.widget_subset_groups.options = options
        self.widget_subset_groups.index = tuple(indices)

    def _set_subset_groups(self, change):
        subset_groups = [self.data_collection.subset_groups[k] for k in self.widget_subset_groups.index]
        self.session.edit_subset_mode.edit_subset = subset_groups

    def _set_selection_mode(self, change):
        #EditSubsetMode().mode = self.selection_modes[change.new][1]
        self.subset_mode(self.selection_modes[change.new][1])

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

    def histogram1d(self, x, data=None, widget='bqplot'):
        if widget == 'bqplot':
            from .bqplot import BqplotHistogramView
            viewer_cls = BqplotHistogramView
        elif widget == 'matplotlib':
            from .matplotlib.histogram import HistogramJupyterViewer
            viewer_cls = HistogramJupyterViewer
        else:
            raise ValueError("Widget type should be 'bqplot' or 'matplotlib'")
        data = data or self._data[0]
        view = self.new_data_viewer(viewer_cls, data=data)
        x = data.id[x]
        view.state.x_att = x
        return view

    def scatter2d(self, x, y, data=None, widget='bqplot'):
        if widget == 'bqplot':
            from .bqplot import BqplotScatterView
            viewer_cls = BqplotScatterView
        elif widget == 'matplotlib':
            from .matplotlib.scatter import ScatterJupyterViewer
            viewer_cls = ScatterJupyterViewer
        else:
            raise ValueError("Widget type should be 'bqplot' or 'matplotlib'")
        data = data or self._data[0]
        view = self.new_data_viewer(viewer_cls, data=data)
        x = data.id[x]
        y = data.id[y]
        view.state.x_att = x
        view.state.y_att = y
        return view

    def scatter3d(self, x, y, z, data=None):
        from .ipyvolume import IpyvolumeScatterView
        data = data or self._data[0]
        view = self.new_data_viewer(IpyvolumeScatterView, data=data)
        x = data.id[x]
        y = data.id[y]
        z = data.id[z]
        view.state.x_att = x
        view.state.y_att = y
        view.state.z_att = z
        return view

    def imshow(self, x="Pixel Axis 1 [x]", y="Pixel Axis 0 [y]", data=None, widget='bqplot'):
        if widget == 'bqplot':
            from .bqplot import BqplotImageView
            viewer_cls = BqplotImageView
        elif widget == 'matplotlib':
            from .matplotlib.image import ImageJupyterViewer
            viewer_cls = ImageJupyterViewer
        else:
            raise ValueError("Widget type should be 'bqplot' or 'matplotlib'")
        data = data or self._data[0]
        view = self.new_data_viewer(viewer_cls, data=data)
        x = data.id[x]
        y = data.id[y]
        view.state.x_att = x
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
        x = data.id[x]
        view.state.x_att = x
        return view

    def volshow(self, x="Pixel Axis 2 [x]", y="Pixel Axis 1 [y]", z="Pixel Axis 0 [z]", data=None):
        from .ipyvolume import IpyvolumeVolumeView
        data = data or self._data[0]
        view = self.new_data_viewer(IpyvolumeVolumeView, data=data)
        x = data.id[x]
        y = data.id[y]
        z = data.id[z]
        view.state.x_att = x
        view.state.y_att = y
        view.state.z_att = z
        return view

    def subset(self, name, state):
        return self.data_collection.new_subset_group(name, state)

    def _update_undo_redo_enabled(self, *args):
        pass  # TODO: if we want a gui for this, we need to update it here


class IPyWidgetLayerArtistContainer(LayerArtistContainer):

    def __init__(self):
        super(IPyWidgetLayerArtistContainer, self).__init__()
        pass  #print('layer artist created')


class IPyWidgetView(Viewer):

    _layer_artist_container_cls = IPyWidgetLayerArtistContainer

    def __init__(self, session):
        super(IPyWidgetView, self).__init__(session)

    # TODO: a lot of this comes from DataViewerWithState
    def register_to_hub(self, hub):
        super(IPyWidgetView, self).register_to_hub(hub)

        hub.subscribe(self, msg.SubsetCreateMessage,
                      handler=self._add_subset,
                      filter=self._subset_has_data)

        hub.subscribe(self, msg.SubsetUpdateMessage,
                      handler=self._update_subset,
                      filter=self._has_data_or_subset)

        hub.subscribe(self, msg.SubsetDeleteMessage,
                      handler=self._remove_subset,
                      filter=self._has_data_or_subset)

        hub.subscribe(self, msg.NumericalDataChangedMessage,
                      handler=self._update_data,
                      filter=self._has_data_or_subset)

        # hub.subscribe(self, msg.DataCollectionDeleteMessage,
        #               handler=self._remove_data)

        hub.subscribe(self, msg.ComponentsChangedMessage,
                      handler=self._update_data,
                      filter=self._has_data_or_subset)

        # hub.subscribe(self, msg.SettingsChangeMessage,
        #               self._update_appearance_from_settings,
        #               filter=self._is_appearance_settings)


    def remove_subset(self, subset):
        if subset in self._layer_artist_container:
            self._layer_artist_container.pop(subset)
            self.redraw()

    def _remove_subset(self, message):
        self.remove_subset(message.subset)

    def _add_subset(self, message):
        self.add_subset(message.subset)

    def _update_subset(self, message):
        if message.subset in self._layer_artist_container:
            for layer_artist in self._layer_artist_container[message.subset]:
                if isinstance(message, msg.SubsetUpdateMessage) and message.attribute not in ['subset_state']:
                    pass
                else:
                    layer_artist.update()
            self.redraw()

    def _subset_has_data(self, x):
        return x.sender.data in self._layer_artist_container.layers

    def _has_data_or_subset(self, x):
        return x.sender in self._layer_artist_container.layers

    def get_layer_artist(self, cls, layer=None, layer_state=None):
        return cls(self, self.state, layer=layer, layer_state=layer_state)

    def _update_data(self, message):
        if message.data in self._layer_artist_container:
            for layer_artist in self._layer_artist_container:
                if isinstance(layer_artist.layer, Subset):
                    if layer_artist.layer.data is message.data:
                        layer_artist.update()
                else:
                    if layer_artist.layer is message.data:
                        layer_artist.update()
            self.redraw()

    def _add_layer_tab(self, layer):
        layer_tab = layer.create_widgets()
        self.tab.children = self.tab.children + (layer_tab, )
        self.tab.set_title(len(self.tab.children)-1, layer.layer.label)
