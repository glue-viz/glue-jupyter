import numpy as np
import ipyvolume

from glue.core.data import Subset
from glue.viewers.common.layer_artist import LayerArtist
from glue.core.data_combo_helper import ComponentIDComboHelper
from glue.core.exceptions import IncompatibleAttribute
from glue.viewers.scatter.state import ScatterLayerState
from echo import CallbackProperty, SelectionCallbackProperty
from glue.utils import ensure_numerical, color2hex

from ...link import link, on_change

__all__ = ['Scatter3DLayerState', 'IpyvolumeScatterLayerArtist']


class Scatter3DLayerState(ScatterLayerState):

    # FIXME: the following should be a SelectionCallbackProperty
    geo = CallbackProperty('diamond', docstring="Type of marker")
    vz_att = SelectionCallbackProperty(docstring="The attribute to use for the z vector arrow")

    def __init__(self, viewer_state=None, layer=None, **kwargs):
        self.vz_att_helper = ComponentIDComboHelper(self, 'vz_att',
                                                    numeric=True, categorical=False)
        super(Scatter3DLayerState, self).__init__(viewer_state=viewer_state, layer=layer)
        # self.update_from_dict(kwargs)

    def _on_layer_change(self, layer=None):
        super(Scatter3DLayerState, self)._on_layer_change(layer=layer)
        if self.layer is None:
            self.vz_att_helper.set_multiple_data([])
        else:
            self.vz_att_helper.set_multiple_data([self.layer])


class IpyvolumeScatterLayerArtist(LayerArtist):

    _layer_state_cls = Scatter3DLayerState

    def __init__(self, view, viewer_state, layer, layer_state):

        super(IpyvolumeScatterLayerArtist, self).__init__(viewer_state,
                                                          layer_state=layer_state,
                                                          layer=layer)

        self.view = view

        self.scatter = ipyvolume.Scatter(x=[0, 1], y=[0, 1], z=[0, 1], color='green',
                                         color_selected='orange', size_selected=7, size=5,
                                         geo='box')
        self.quiver = ipyvolume.Scatter(x=[0, 1], y=[0, 1], z=[0, 1], color='green',
                                        color_selected='orange', size_selected=7, size=5,
                                        geo='arrow', visible=False)
        self.view.figure.scatters = list(self.view.figure.scatters) + [self.scatter, self.quiver]

        on_change([(self.state, 'cmap_mode', 'cmap_att',
                    'cmap_vmin', 'cmap_vmax', 'cmap', 'color')])(self._update_color)
        on_change([(self.state, 'size', 'size_scaling',
                    'size_mode', 'size_vmin', 'size_vmax')])(self._update_size)

        viewer_state.add_callback('x_att', self._update_xyz_att)
        viewer_state.add_callback('y_att', self._update_xyz_att)
        viewer_state.add_callback('z_att', self._update_xyz_att)
        self._update_color()

        link((self.state, 'visible'), (self.scatter.material, 'visible'))

        on_change([(self.state, 'vector_visible', 'vx_att',
                    'vy_att', 'vz_att')])(self._update_quiver)
        link((self.state, 'vector_visible'), (self.quiver, 'visible'))

        link((self.state, 'geo'), (self.scatter, 'geo'))

    def _update_color(self, ignore=None):
        cmap = self.state.cmap
        if self.state.cmap_mode == 'Linear':
            values = self.layer.data[self.state.cmap_att].astype(np.float32).ravel()
            normalized_values = ((values - self.state.cmap_vmin)
                                 / (self.state.cmap_vmax - self.state.cmap_vmin))
            color_values = cmap(normalized_values).astype(np.float32)
            self.scatter.color = color_values
        else:
            self.scatter.color = color2hex(self.state.color)
        # for ipyvolume we set all colors the same, and resize unselected points to 0
        self.quiver.color = self.scatter.color
        self.scatter.color_selected = self.scatter.color
        self.quiver.color_selected = self.quiver.color

    def _update_xyz_att(self, *args):
        self.update()

    def _cast_to_float(self, arr):
        if np.issubdtype(arr.dtype, np.floating):
            return arr

        # `itemsize` returns the byte size of the dtype
        size = 8 * arr.dtype.itemsize
        return arr.astype(f"float{size}")

    def redraw(self):
        pass

    def update(self):
        # we don't use layer, but layer.data to get everything
        self.scatter.z = self._cast_to_float(
                ensure_numerical(self.layer.data[self._viewer_state.x_att]).ravel())
        self.scatter.y = self._cast_to_float(
                ensure_numerical(self.layer.data[self._viewer_state.z_att]).ravel())
        self.scatter.x = self._cast_to_float(
                ensure_numerical(self.layer.data[self._viewer_state.y_att]).ravel())
        self.quiver.x = self.scatter.x
        self.quiver.z = self.scatter.y
        self.quiver.y = self.scatter.z
        if isinstance(self.layer, Subset):

            try:
                mask = self.layer.to_mask()
            except IncompatibleAttribute:
                self.disable("Could not compute subset")
                self._clear_selection()
                return

            selected_indices = np.nonzero(mask)[0]

            self.scatter.selected = selected_indices
            self.quiver.selected = selected_indices

        self._update_size()

    def _clear_selection(self):
        self.scatter.selected = np.array([])
        self.quiver.selected = np.array([])

    def _update_quiver(self):
        with self.quiver.hold_sync():
            self.quiver.vz = self.layer.data[self.state.vx_att].ravel()
            self.quiver.vy = self.layer.data[self.state.vz_att].ravel()
            self.quiver.vx = self.layer.data[self.state.vy_att].ravel()

    def _update_size(self):
        size = self.state.size
        scale = self.state.size_scaling / 5  # /5 seems to give similar sizes as the Qt Glue
        if self.state.size_mode == 'Linear':
            size = self.layer.data[self.state.size_att].ravel()
            size = (size - self.state.size_vmin) / (self.state.size_vmax - self.state.size_vmin)
            size *= 5
        value = size * scale
        if isinstance(self.layer, Subset):
            self.scatter.size = 0
            self.scatter.size_selected = value
        else:
            self.scatter.size = value
            self.scatter.size_selected = value

        value = self.state.size * scale * 5
        if isinstance(self.layer, Subset):
            self.quiver.size = 0
            self.quiver.size_selected = value
        else:
            self.quiver.size = value
            self.quiver.size_selected = value
