import uuid

import numpy as np
import bqplot
import ipywidgets as widgets
import ipywidgets.widgets.trait_types as tt
from IPython.display import display
import matplotlib.cm

from glue.core.layer_artist import LayerArtistBase
from glue.core.data import Subset
from glue.viewers.image.state import ImageLayerState
from glue.viewers.image.layer_artist import ImageLayerArtist

from ..link import link
from .scatter import BqplotScatterLayerArtist

# FIXME: monkey patch ipywidget to accept anything
tt.Color.validate = lambda self, obj, value: value



from .. import IPyWidgetView

# def convert_color(color):
#     #if color == 'green':
#     #    return color
#     return '#777'


def _mask_to_png_data(mask, color):
    r, g, b = matplotlib.colors.to_rgb(color)
    rgba = np.zeros(mask.shape + (4,), dtype=np.uint8)
    print(rgba.shape)
    rgba[mask.astype(np.bool),3] = 0.5 * 255
    rgba[...,0:3] = r * 255, g * 255, b * 255
    return _rgba_to_png_data(rgba)

class BqplotImageLayerArtist(LayerArtistBase):
    _layer_state_cls = ImageLayerState

    get_layer_color = ImageLayerArtist.get_layer_color
    get_image_shape = ImageLayerArtist.get_image_shape
    get_image_data  = ImageLayerArtist.get_image_data
    _update_visual_attributes = ImageLayerArtist._update_visual_attributes
    _update_compatibility = ImageLayerArtist._update_compatibility

    def __init__(self, view, viewer_state, layer, layer_state):
        super(BqplotImageLayerArtist, self).__init__(layer)
        self.view = view
        self.state = layer_state or self._layer_state_cls(viewer_state=viewer_state,
                                                          layer=self.layer)
        self._viewer_state = viewer_state
        if self.state not in self._viewer_state.layers:
            self._viewer_state.layers.append(self.state)

        self._update_compatibility()

        self.uuid = str(uuid.uuid4())
        self.composite = self.view.composite
        self.composite.allocate(self.uuid)
        self.composite.set(self.uuid, array=self.get_image_data,
                           shape=self.get_image_shape)
        viewer_state.add_callback('x_att', self._update_xy_att)
        viewer_state.add_callback('y_att', self._update_xy_att)

    def _update_xy_att(self, *args):
        self.update()

    def redraw(self):
        self.update()

    def clear(self):
        pass

    def _workaround_unselected_style(self, change):
        # see https://github.com/bloomberg/bqplot/issues/606
        if hasattr(self.layer, 'to_mask'):  # TODO: what is the best way to test if it is Data or Subset?
            self.image.unselected_style = {'fill': 'white', 'stroke': 'none'}
            self.image.unselected_style = {'fill': 'none', 'stroke': 'none'}

    def update(self):
        self._update_visual_attributes()
        self.view.update_composite()

    def _update_visual_attributes(self):
        # TODO: refactor since this is almost a copy of glue.viewers.image.layer_artist

        if not self.enabled:
            return

        if self._viewer_state.color_mode == 'Colormaps':
            color = self.state.cmap
        else:
            color = self.state.color

        self.composite.set(self.uuid,
                           clim=(self.state.v_min, self.state.v_max),
                           visible=self.state.visible,
                           zorder=self.state.zorder,
                           color=color,
                           contrast=self.state.contrast,
                           bias=self.state.bias,
                           alpha=self.state.alpha,
                           stretch=self.state.stretch)

        #self.redraw()
