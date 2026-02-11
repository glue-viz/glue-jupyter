import ipyvolume as ipv
import numpy as np
import matplotlib.colors

from glue.viewers.common.layer_artist import LayerArtist
from glue.core.data import Subset
from glue.core.exceptions import IncompatibleAttribute

from .layer_state import VolumeLayerState
from ...link import link, dlink, on_change

__all__ = ['IpyvolumeVolumeLayerArtist']


def _transfer_func_rgba(color, N=256, max_opacity=1, stretch=None):
    r, g, b = matplotlib.colors.to_rgb(color)
    data = np.zeros((N, 4), dtype=np.float32)
    ramp = np.linspace(0, 1, N)
    if stretch is not None:
        ramp = stretch(ramp)
    data[..., 0] = r
    data[..., 1] = g
    data[..., 2] = b
    data[..., 3] = ramp*max_opacity
    return data


def _transfer_func_cmap(cmap, N=256, max_opacity=1, stretch=None):
    data = np.zeros((N, 4), dtype=np.float32)
    ramp = np.linspace(0, 1, N)
    if stretch is not None:
        ramp = stretch(ramp)
    colors = cmap(ramp)
    for i in range(3):
        data[..., i] = [c[i] for c in colors]
    data[..., 3] = ramp*max_opacity
    return data


data0 = [[[1, 2]] * 2] * 2


class IpyvolumeVolumeLayerArtist(LayerArtist):

    _layer_state_cls = VolumeLayerState

    def __init__(self, view, viewer_state, layer=None, layer_state=None):

        super(IpyvolumeVolumeLayerArtist, self).__init__(viewer_state,
                                                         layer_state=layer_state,
                                                         layer=layer)

        self.view = view
        self.figure = view.figure

        self.transfer_function = ipv.TransferFunction(rgba=_transfer_func_rgba(self.state.color))
        self.volume = ipv.Volume(extent_original=[[0, 1]] * 3, data_original=data0,
                                 tf=self.transfer_function, data_max_shape=128)
        self.figure.volumes = self.figure.volumes + [self.volume]

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

        on_change([(self.state, 'color', 'alpha', 'color_mode',
                    'cmap', 'stretch', 'stretch_parameters'
                    )])(self._update_transfer_function)

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

        data = np.transpose(data, (2, 0, 1))
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
        def stretch(x):
            return self.state.stretch_object(x, **self.state.stretch_parameters)
        if self.state.color_mode == "Fixed":
            self.transfer_function.rgba = _transfer_func_rgba(self.state.color,
                                                              max_opacity=self.state.alpha,
                                                              stretch=stretch)
        else:
            self.transfer_function.rgba = _transfer_func_cmap(self.state.cmap,
                                                              max_opacity=self.state.alpha,
                                                              stretch=stretch)
