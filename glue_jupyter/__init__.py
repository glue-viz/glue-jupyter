from glue.core import message as msg
from glue.core.application_base import ViewerBase
from glue.core.layer_artist import LayerArtistContainer
from glue.core.edit_subset_mode import (EditSubsetMode, OrMode, AndNotMode,
                                        AndMode, XorMode, ReplaceMode)
from IPython.display import display
import ipywidgets as widgets
# from glue.core.session import Session
# from glue.viewers.scatter.layer_artist import ScatterLayerArtist


def jglue(*args, **kwargs):
    from glue.core import DataCollection
    from glue.app.qt import GlueApplication
    from glue.qglue import parse_data, parse_links

    links = kwargs.pop('links', None)

    dc = DataCollection()
    for label, data in kwargs.items():
        dc.extend(parse_data(data, label))
    for data in args:
        dc.append(data)

    if links is not None:
        dc.add_link(parse_links(dc, links))

    japp = JupyterApplication(dc)
    return japp

def example_data_xyz(seed=42, N=500):
    from glue.core import Data
    import numpy as np
    rng = np.random.RandomState(seed)
    x, y, z = rng.normal(size=(3, N))
    data_xyz = Data(x=x, y=y, z=z, label="xyz data")
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
        self.widget = widgets.VBox(children=[self.widget_selection_mode])
        self.widget_selection_mode.observe(self._set_selection_mode, 'index')
        display(self.widget)

    def _set_selection_mode(self, change):
        EditSubsetMode().mode = self.selection_modes[change.new][1]

    def add_widget(self, widget, label=None, tab=None):
        pass

    def histogram1d(self, x, data=None):
        from .bqplot import BqplotHistogramView
        data = data or self._data[0]
        view = self.new_data_viewer(BqplotHistogramView, data=data)
        x = data.id[x]
        view.state.x_att = x
        return view


    def scatter2d(self, x, y, data=None):
        from .bqplot import BqplotScatterView
        data = data or self._data[0]
        view = self.new_data_viewer(BqplotScatterView, data=data)
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

    def volume3d(self, x="Pixel Axis 2 [x]", y="Pixel Axis 1 [y]", z="Pixel Axis 0 [z]", data=None):
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

    def _update_undo_redo_enabled(self):
        pass  # TODO: if we want a gui for this, we need to update it here


class IPyWidgetLayerArtistContainer(LayerArtistContainer):

    def __init__(self):
        super(IPyWidgetLayerArtistContainer, self).__init__()
        pass  #print('layer artist created')


class IPyWidgetView(ViewerBase):

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
                layer_artist.update()
            self.redraw()

    def _subset_has_data(self, x):
        return x.sender.data in self._layer_artist_container.layers

    def _has_data_or_subset(self, x):
        return x.sender in self._layer_artist_container.layers

    def get_layer_artist(self, cls, layer=None, layer_state=None):
        return cls(self, self.state, layer=layer, layer_state=layer_state)

    def _update_data(self, message):
        print('update data', message)
        if message.data in self._layer_artist_container:
            for layer_artist in self._layer_artist_container:
                if isinstance(layer_artist.layer, Subset):
                    if layer_artist.layer.data is message.data:
                        layer_artist.update()
                else:
                    if layer_artist.layer is message.data:
                        layer_artist.update()
            self.redraw()

