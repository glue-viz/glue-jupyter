import ipyvolume as ipv
import numpy as np
import matplotlib.colors

from glue_vispy_viewers.volume.layer_state import VolumeLayerState
from echo import CallbackProperty
from glue.core.data import Subset
from glue.core.exceptions import IncompatibleAttribute
from glue_vispy_viewers.common.layer_artist import VispyLayerArtist

from ...link import link, dlink, on_change

__all__ = ['VolumeLayerState']


class VolumeLayerState(VolumeLayerState):

    opacity_scale = CallbackProperty()
    render_method = CallbackProperty()
    lighting = CallbackProperty()
    max_resolution = CallbackProperty()
    clamp_min = CallbackProperty()
    clamp_max = CallbackProperty()
    # attribute = SelectionCallbackProperty()

    data_min = CallbackProperty(0)
    data_max = CallbackProperty(1)

    def __init__(self, layer=None, **kwargs):
        super(VolumeLayerState, self).__init__(layer=layer, **kwargs)
        self.opacity_scale = 0.1
        self.render_method = 'NORMAL'
        self.lighting = True
        self.max_resolution = 256
        self.clamp_min = False
        self.clamp_max = False


def _transfer_func_rgba(color, N=256, max_opacity=1):
    r, g, b = matplotlib.colors.to_rgb(color)
    data = np.zeros((N, 4), dtype=np.float32)
    ramp = np.linspace(0, 1, N)
    data[..., 0] = r
    data[..., 1] = g
    data[..., 2] = b
    data[..., 3] = ramp*max_opacity
    return data


data0 = [[[1, 2]] * 2] * 2


class IpyvolumeVolumeLayerArtist(VispyLayerArtist):
    def __init__(self, ipyvolume_viewer=None, state=None, layer=None, layer_state=None):
        super(IpyvolumeVolumeLayerArtist, self).__init__(layer)
        self.layer = layer or layer_state.layer
        self.ipyvolume_viewer = ipyvolume_viewer
        self.figure = self.ipyvolume_viewer.figure
        self.state = layer_state or VolumeLayerState(layer=self.layer)
        self.transfer_function = ipv.TransferFunction(rgba=_transfer_func_rgba(self.state.color))
        self.volume = ipv.Volume(extent_original=[[0, 1]] * 3, data_original=data0,
                                 tf=self.transfer_function, data_max_shape=128)
        self.figure.volumes = self.figure.volumes + [self.volume]
        self._viewer_state = ipyvolume_viewer.state
        assert ipyvolume_viewer.state == state
        if self.state not in self._viewer_state.layers:
            self._viewer_state.layers.append(self.state)

        # ipv.figure(self.ipyvolume_viewer.figure)
        self.last_shape = None

        dlink((self.state, 'lighting'), (self.volume, 'lighting'))
        dlink((self.state, 'render_method'), (self.volume, 'rendering_method'))
        dlink((self.state, 'max_resolution'), (self.volume, 'data_max_shape'))

        dlink((self.state, 'vmin'), (self.volume, 'show_min'))
        dlink((self.state, 'vmax'), (self.volume, 'show_max'))

        dlink((self.state, 'data_min'), (self.volume, 'data_min'))
        dlink((self.state, 'data_max'), (self.volume, 'data_max'))

        dlink((self.state, 'clamp_min'), (self.volume, 'clamp_min'))
        dlink((self.state, 'clamp_max'), (self.volume, 'clamp_max'))

        link((self.state, 'opacity_scale'), (self.volume, 'opacity_scale'))

        on_change([(self.state, 'color', 'alpha')])(self._update_transfer_function)

    def clear(self):
        pass

    def redraw(self):
        pass

    def update(self):
        if isinstance(self.layer, Subset):
            try:
                mask = self.layer.to_mask()
            except IncompatibleAttribute:
                # The following includes a call to self.clear()
                self.disable("Subset cannot be applied to this data")
                return
            else:
                self.enable()
            data = self.layer.data[self.state.attribute].astype(np.float32)
            data *= mask
        else:
            data = self.layer[self.state.attribute]
        finite_mask = np.isfinite(data)
        finite_data = data[finite_mask]
        finite_mask_normalized = finite_data - finite_data.min()
        finite_mask_normalized = finite_mask_normalized / finite_mask_normalized.max()

        data_min, data_max = np.nanmin(data), np.nanmax(data)

        self.last_shape = shape = data.shape
        if self.volume is None:
            with self.figure:
                self.volume = ipv.volshow(data, data_min=data_min, data_max=data_max,
                                          extent=[[0, shape[0]], [0, shape[1]], [0, shape[2]]],
                                          controls=False, tf=self.transfer_function)
        else:
            self.volume.extent_original = [[0, shape[0]], [0, shape[1]], [0, shape[2]]]
            self.volume.data_original = data
            self.volume.data_min = data_min
            self.volume.data_max = data_max
        self.state.data_min = self.state.vmin
        self.state.data_max = self.state.vmax

        # might be a bug in glue-core, it seems that for subsets vmin/vmax are
        # not calculated
        if self.state.vmin == self.state.vmax == 0:
            self.state.lim_helper.log = False
            self.state.percentile = 100

    def _update_transfer_function(self):
        self.transfer_function.rgba = _transfer_func_rgba(self.state.color,
                                                          max_opacity=self.state.alpha)
