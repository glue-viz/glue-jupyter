import numpy as np
import bqplot
from ..compatibility import ScatterGL, ImageGL

from glue.core.data import Subset
from glue.viewers.scatter.state import ScatterLayerState
from glue.core.exceptions import IncompatibleAttribute
from glue.viewers.common.layer_artist import LayerArtist

from ...link import dlink, on_change
from ...utils import colormap_to_hexlist, debounced, float_or_none
from echo import CallbackProperty
from glue.utils import ensure_numerical, color2hex

__all__ = ['BqplotScatterLayerState', 'BqplotScatterLayerArtist']
EMPTY_IMAGE = np.zeros((10, 10, 4), dtype=np.uint8)


class BqplotScatterLayerState(ScatterLayerState):
    bins = CallbackProperty(128, docstring='The number of bins in each dimension '
                                           'for the density map')


class BqplotScatterLayerArtist(LayerArtist):
    _layer_state_cls = BqplotScatterLayerState

    def __init__(self, view, viewer_state, layer_state=None, layer=None):

        super(BqplotScatterLayerArtist, self).__init__(viewer_state,
                                                       layer_state=layer_state, layer=layer)

        self.view = view

        self.scale_size = bqplot.LinearScale()
        self.scale_color = bqplot.ColorScale()
        self.scale_size_quiver = bqplot.LinearScale(min=0, max=1)
        self.scale_rotation = bqplot.LinearScale(min=0, max=1)
        self.scales = dict(self.view.scales, size=self.scale_size,
                           rotation=self.scale_rotation, color=self.scale_color)
        self.scale_image = bqplot.ColorScale()
        self.scales_quiver = dict(self.view.scales, size=self.scale_size_quiver,
                                  rotation=self.scale_rotation)
        self.scales_image = dict(self.view.scales, image=self.scale_image)
        self.scatter = ScatterGL(scales=self.scales, x=[0, 1], y=[0, 1])
        self.quiver = ScatterGL(scales=self.scales_quiver, x=[0, 1], y=[0, 1],
                                visible=False, marker='arrow')

        self.counts = None
        self.image = ImageGL(scales=self.scales_image, image=EMPTY_IMAGE)
        on_change([(self.state, 'density_map')])(self._on_change_density_map)
        on_change([(self.state, 'bins')])(self._update_scatter)
        self._viewer_state.add_global_callback(self._update_scatter)

        self.view.figure.marks = (list(self.view.figure.marks)
                                  + [self.image, self.scatter, self.quiver])
        dlink((self.state, 'color'), (self.scatter, 'colors'), lambda x: [color2hex(x)])
        dlink((self.state, 'color'), (self.quiver, 'colors'), lambda x: [color2hex(x)])
        self.scatter.observe(self._workaround_unselected_style, 'colors')
        self.quiver.observe(self._workaround_unselected_style, 'colors')

        on_change([(self.state, 'cmap_mode', 'cmap_att')])(self._on_change_cmap_mode_or_att)
        on_change([(self.state, 'cmap')])(self._on_change_cmap)
        dlink((self.state, 'cmap_vmin'), (self.scale_color, 'min'), float_or_none)
        dlink((self.state, 'cmap_vmax'), (self.scale_color, 'max'), float_or_none)

        on_change([(self.state, 'size', 'size_scaling', 'size_mode',
                    'size_vmin', 'size_vmax')])(self._update_size)

        viewer_state.add_callback('x_att', self._update_xy_att)
        viewer_state.add_callback('y_att', self._update_xy_att)
        self._update_size()
        # set initial values for the colormap
        self._on_change_cmap()

        self.state.add_callback('visible', self._update_visibility)
        self.state.add_callback('vector_visible', self._update_visibility)
        self.state.add_callback('density_map', self._update_visibility)

        self.state.add_callback('zorder', self._update_zorder)

        dlink((self.state, 'visible'), (self.scatter, 'visible'))
        dlink((self.state, 'visible'), (self.image, 'visible'))

        dlink((self.state, 'alpha'), (self.scatter, 'opacities'), lambda x: [x])
        dlink((self.state, 'alpha'), (self.quiver, 'opacities'), lambda x: [x])
        dlink((self.state, 'alpha'), (self.image, 'opacity'))

        dlink((self.state, 'fill'), (self.scatter, 'fill'))

        on_change([(self.state, 'vector_visible', 'vx_att', 'vy_att')])(self._update_quiver)
        dlink((self.state, 'vector_visible'), (self.quiver, 'visible'))

    def remove(self):
        marks = self.view.figure.marks[:]
        marks.remove(self.image)
        self.image = None
        marks.remove(self.scatter)
        self.scatter = None
        marks.remove(self.quiver)
        self.quiver = None
        self.view.figure.marks = marks
        return super().remove()

    def _update_xy_att(self, *args):
        self.update()

    def _on_change_cmap_mode_or_att(self, ignore=None):
        if self.state.cmap_mode == 'Linear' and self.state.cmap_att is not None:
            self.scatter.color = self.layer.data[self.state.cmap_att].astype(np.float32).ravel()
        else:
            self.scatter.color = None

    def _on_change_cmap(self, ignore=None):
        cmap = self.state.cmap
        colors = colormap_to_hexlist(cmap)
        self.scale_color.colors = colors

    def _on_change_density_map(self):
        self._update_visibility()
        self._update_scatter()

    def _update_visibility(self, *args):
        self.image.visible = self.state.density_map
        self.scatter.visible = not self.state.density_map
        self.quiver.visible = not self.state.density_map and self.state.vector_visible

    def _update_zorder(self, *args):
        sorted_layers = sorted(self.view.layers, key=lambda layer: layer.state.zorder)
        self.view.figure.marks = [item for layer in sorted_layers
                                  for item in (layer.image, layer.scatter, layer.quiver)]

    def redraw(self):
        self.update()

    def _workaround_unselected_style(self, change=None):
        # see https://github.com/bloomberg/bqplot/issues/606
        if isinstance(self.layer, Subset):
            self.scatter.unselected_style = {'fill': 'white', 'stroke': 'none'}
            self.scatter.unselected_style = {'fill': 'none', 'stroke': 'none'}
            self.quiver.unselected_style = {'fill': 'white', 'stroke': 'none'}
            self.quiver.unselected_style = {'fill': 'none', 'stroke': 'none'}

    @debounced(method=True)
    def update_histogram(self):
        if isinstance(self.layer, Subset):
            data = self.layer.data
            subset_state = self.layer.subset_state
        else:
            data = self.layer
            subset_state = None
        if self.state.density_map:
            bins = [self.state.bins, self.state.bins]
            range_x = [self.view.scale_x.min, self.view.scale_x.max]
            range_y = [self.view.scale_y.min, self.view.scale_y.max]
            range = [range_x, range_y]
            self.counts = data.compute_histogram([self._viewer_state.x_att,
                                                  self._viewer_state.y_att],
                                                 subset_state=subset_state,
                                                 bins=bins, range=range)
            self.scale_image.min = 0
            self.scale_image.max = np.nanmax(self.counts).item()
            with self.image.hold_sync():
                self.image.x = range_x
                self.image.y = range_y
                self.image.image = self.counts.T.astype(np.float32, copy=True)

    def _update_scatter(self, **changes):
        self.update_histogram()
        self.update()

    def update(self):

        if (self.image is None or
                self.scatter is None or
                self.quiver is None or
                self._viewer_state.x_att is None or
                self._viewer_state.y_att is None or
                self.state.layer is None):
            return

        if self.state.density_map:
            pass
        else:
            self.scatter.x = (ensure_numerical(self.layer.data[self._viewer_state.x_att])
                              .astype(np.float32).ravel())
            self.scatter.y = (ensure_numerical(self.layer.data[self._viewer_state.y_att])
                              .astype(np.float32).ravel())
            self.quiver.x = self.scatter.x
            self.quiver.y = self.scatter.y

        if isinstance(self.layer, Subset):

            try:
                mask = self.layer.to_mask()
            except IncompatibleAttribute:
                self.disable("Could not compute subset")
                self._clear_selection()
                return

            selected_indices = np.nonzero(mask)[0].tolist()

            self.scatter.selected = selected_indices
            self.scatter.selected_style = {}
            self.scatter.unselected_style = {'fill': 'none', 'stroke': 'none'}
            self.quiver.selected = selected_indices
            self.quiver.selected_style = {}
            self.quiver.unselected_style = {'fill': 'none', 'stroke': 'none'}

        else:
            self._clear_selection()

    def _clear_selection(self):
        self.scatter.selected = None
        self.scatter.selected_style = {}
        self.scatter.unselected_style = {}
        self.quiver.selected = None
        self.quiver.selected_style = {}
        self.quiver.unselected_style = {}

    def _update_quiver(self):

        if (not self.state.vector_visible
                or self.state.vx_att is None
                or self.state.vy_att is None):
            return

        size = 50
        scale = 1
        self.quiver.default_size = int(size * scale * 4)
        vx = self.layer.data[self.state.vx_att].ravel()
        vy = self.layer.data[self.state.vy_att].ravel()
        length = np.sqrt(vx**2 + vy**2)
        self.scale_size_quiver.min = np.nanmin(length)
        self.scale_size_quiver.max = np.nanmax(length)
        self.quiver.size = length
        angle = np.arctan2(vy, vx)
        self.scale_rotation.min = -np.pi
        self.scale_rotation.max = np.pi
        self.quiver.rotation = angle

    def _update_size(self):

        size = self.state.size
        scale = self.state.size_scaling
        if self.state.size_mode == 'Linear' and self.state.size_att is not None:
            self.scatter.default_size = int(scale * 25)
            self.scatter.size = self.layer.data[self.state.size_att].ravel()
            self.scale_size.min = float_or_none(self.state.size_vmin)
            self.scale_size.max = float_or_none(self.state.size_vmax)
            self._workaround_unselected_style()
        else:
            self.scatter.default_size = int(size * scale)
            self.scatter.size = None
            self.scale_size.min = 0
            self.scale_size.max = 1
