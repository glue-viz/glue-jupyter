import ipyvolume as ipv
import ipywidgets as widgets
import traitlets
from IPython.display import display
import numpy as np
import matplotlib.colors

from .scatter import IpyvolumeScatterLayerArtist
from ..utils import reduce_size

#from glue_vispy_viewers.common.layer_state import VispyLayerState
from glue_vispy_viewers.volume.layer_state import VolumeLayerState
from glue.core.data_combo_helper import ComponentIDComboHelper
from glue.external.echo import (CallbackProperty, SelectionCallbackProperty)
from glue.core.data import Subset
from glue.core.exceptions import IncompatibleAttribute

from ..link import link, dlink, calculation, link_component_id_to_select_widget, on_change

class IpyvolumeLayerState(VolumeLayerState):
    pass
    opacity_scale = CallbackProperty()
    # attribute = SelectionCallbackProperty()

    def __init__(self, layer=None, **kwargs):
        super(IpyvolumeLayerState, self).__init__(layer=layer)
        self.opacity_scale = 0.1



from glue_vispy_viewers.common.layer_artist import VispyLayerArtist

def _transfer_function_rgba(color, N=256, max_opacity=1):
    r, g, b = matplotlib.colors.to_rgb(color)
    data = np.zeros((N, 4), dtype=np.float32)
    ramp = np.linspace(0, 1, N)
    data[...,0] = r
    data[...,1] = g
    data[...,2] = b
    data[...,3] = ramp*max_opacity
    return data

class IpyvolumeVolumeLayerArtist(VispyLayerArtist):
    def __init__(self, ipyvolume_viewer=None, state=None, layer=None, layer_state=None):
        super(IpyvolumeVolumeLayerArtist, self).__init__(layer)
        self.layer = layer or layer_state.layer
        self.ipyvolume_viewer = ipyvolume_viewer
        self.figure = self.ipyvolume_viewer.figure
        self._viewer_state = ipyvolume_viewer.state
        assert ipyvolume_viewer.state == state
        self.state = layer_state or IpyvolumeLayerState(layer=self.layer)
        self.transfer_function = ipv.TransferFunction(rgba=_transfer_function_rgba(self.state.color))
        if self.state not in self._viewer_state.layers:
            self._viewer_state.layers.append(self.state)

        #ipv.figure(self.ipyvolume_viewer.figure)
        self.volume = None
        self.last_shape = None

    def clear(self):
        pass

    def redraw(self):
        pass

    def update(self):
        # print(self.layer)
        if isinstance(self.layer, Subset):
            try:
                mask = self.layer.to_mask()
            except IncompatibleAttribute:
                # The following includes a call to self.clear()
                self.disable("Subset cannot be applied to this data")
                return
            else:
                self._enabled = True
            # if self.state.subset_mode == 'outline':
            #     data = mask.astype(np.float32)
            # else:
            data = self.layer.data[self.state.attribute].astype(np.float32)
            data *= mask
        else:
            data = self.layer[self.state.attribute]
        #data = self.layer.data[self.state.attribute].astype(np.float32)
        #print(data, data.shape, self.state.attribute)
        finite_mask = np.isfinite(data)
        data_min, data_max = np.percentile(
            data[finite_mask], 1), np.percentile(data[finite_mask], 99)
        #data_min, data_max = None, None
        self.last_shape = shape = data.shape
        data = reduce_size(data, self.widget_max_resolution.value)
        if self.volume is None:
            with self.figure:
                self.volume = ipv.volshow(data, data_min=data_min, data_max=data_max, extent=[[0, shape[0]], [0, shape[1]], [0, shape[2]]], controls=False, tf=self.transfer_function)
        else:
            self.ipyvolume_viewer.figure.volume_data = data

    def _update_transfer_function(self):
        self.transfer_function.rgba = _transfer_function_rgba(self.state.color, max_opacity=self.state.alpha)


    def create_widgets(self):
        self.size_options = [128, 128+64, 256, 256+128, 512]
        options = [(str(k), k) for k in self.size_options]
        self.widget_max_resolution = widgets.Dropdown(options=options, value=128, description='max resolution')
        self.widget_color = widgets.ColorPicker(value=self.state.color, description='color')
        link((self.state, 'color'), (self.widget_color, 'value'))

        self.widget_opacity = widgets.FloatSlider(description='opacity', min=0, max=1, value=self.state.alpha, step=0.001)
        link((self.state, 'alpha'), (self.widget_opacity, 'value'))

        self.widget_opacity_scale = widgets.FloatLogSlider(description='opacity scale', base=10, min=-3, max=3, value=self.state.opacity_scale, step=0.01)
        link((self.state, 'opacity_scale'), (self.widget_opacity_scale, 'value'))
        link((self.state, 'opacity_scale'), (self.figure, 'opacity_scale'))

        on_change([(self.state, 'color', 'alpha')])(self._update_transfer_function)

        self.widget_reset_zoom = widgets.Button(description="Reset zoom")
        def reset_zoom(*ignore):
            with self.figure:
                if self.last_shape is not None:
                    ipv.xlim(0, self.last_shape[0])
                    ipv.ylim(0, self.last_shape[1])
                    ipv.zlim(0, self.last_shape[2])
        self.widget_reset_zoom.on_click(reset_zoom)
        return widgets.VBox([self.widget_max_resolution, self.widget_reset_zoom, self.widget_color, self.widget_opacity, self.widget_opacity_scale])

#from glue_vispy_viewers.common.vispy_data_viewer import BaseVispyViewer


#$IpyvolumeVolumeView.get_data_layer_artist = DataViewerWithState.get_data_layer_artist
