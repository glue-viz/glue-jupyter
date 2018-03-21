import numpy as np
import bqplot
import ipywidgets as widgets
import ipywidgets.widgets.trait_types as tt
from IPython.display import display
import PIL.Image
import matplotlib.cm
try:
    from io import BytesIO as StringIO # python3
except:
    from StringIO import StringIO # python2

from glue.core.layer_artist import LayerArtistBase
from glue.core.data import Subset
from glue.viewers.image.state import ImageLayerState

from ..link import link
from .scatter import BqplotScatterLayerArtist

# FIXME: monkey patch ipywidget to accept anything
tt.Color.validate = lambda self, obj, value: value



from .. import IPyWidgetView

# def convert_color(color):
#     #if color == 'green':
#     #    return color
#     return '#777'

def _rgba_to_png_data(rgba):
    width, height = rgba.shape[1], rgba.shape[0]
    f = StringIO()
    img = PIL.Image.frombuffer("RGBA", (width, height), rgba, 'raw', 'RGBA', 0, 0)
    img.save(f, "png")
    return f.getvalue()

def _scalar_to_png_data(I, colormap='viridis'):
    mask = ~np.isfinite(I)
    I = np.ma.masked_array(I, mask)
    colormap = matplotlib.cm.get_cmap(colormap)
    colormap.set_bad(alpha=0)
    data = colormap(I, bytes=True)
    return _rgba_to_png_data(data)

def _mask_to_png_data(mask, color):
    r, g, b = matplotlib.colors.to_rgb(color)
    rgba = np.zeros(mask.shape + (4,), dtype=np.uint8)
    print(rgba.shape)
    rgba[mask.astype(np.bool),3] = 0.5 * 255
    rgba[...,0:3] = r * 255, g * 255, b * 255
    return _rgba_to_png_data(rgba)

class BqplotImageLayerArtist(LayerArtistBase):
    _layer_state_cls = ImageLayerState

    def __init__(self, view, viewer_state, layer, layer_state):
        super(BqplotImageLayerArtist, self).__init__(layer)
        self.view = view
        self.state = layer_state or self._layer_state_cls(viewer_state=viewer_state,
                                                          layer=self.layer)
        self._viewer_state = viewer_state
        if self.state not in self._viewer_state.layers:
            self._viewer_state.layers.append(self.state)
        data = np.random.random((32, 32))
        
        self.image_widget = widgets.Image(value=_scalar_to_png_data(data), format='png', width=32, height=32)
        self.image_mark = bqplot.Image(image=self.image_widget,
            scales=self.view.scales, x=[0, 32], y=[0, 32])
        self.view.figure.marks = list(self.view.figure.marks) + [self.image_mark]
        #link((self.image, 'colors'), (self.state, 'color'), lambda x: x[0], lambda x: [x])
        #link((self.image, 'default_opacities'), (self.state, 'alpha'), lambda x: x[0], lambda x: [x])
        #link((self.image, 'default_size'), (self.state, 'size'))
        #self.image.observe(self._workaround_unselected_style, 'colors')

        viewer_state.add_callback('x_att', self._update_xy_att)
        viewer_state.add_callback('y_att', self._update_xy_att)

    def _update_xy_att(self, *args):
        self.update()

    def redraw(self):
        pass
        self.update()
        #self.image.x = self.layer[self._viewer_state.x_att]
        #self.image.y = self.layer[self._viewer_state.y_att]

    def clear(self):
        pass

    def _workaround_unselected_style(self, change):
        # see https://github.com/bloomberg/bqplot/issues/606
        if hasattr(self.layer, 'to_mask'):  # TODO: what is the best way to test if it is Data or Subset?
            self.image.unselected_style = {'fill': 'white', 'stroke': 'none'}
            self.image.unselected_style = {'fill': 'none', 'stroke': 'none'}

    def update(self):
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
            data[~mask] = np.nan
            png_data = _mask_to_png_data(mask, self.state.color)
        else:
            data = self.layer[self.state.attribute]
            data = data - self.state.v_min
            data /= (self.state.v_max - self.state.v_min)
            print(np.nanmin(data), np.nanmax(data))
            png_data = _scalar_to_png_data(data)
        height, width = data.shape
        with self.image_widget.hold_sync():
            self.image_widget.value = png_data
            self.image_widget.width = width
            self.image_widget.height = height
        # force the image mark to update the image data
        self.image_mark.send_state(key='image')
        self.image_mark.x = [0, width]
        self.image_mark.y = [0, height]
        # bug? this will cause a redraw for sure, but why is this needed?
        marks = list(self.view.figure.marks)
        self.view.figure.marks = []
        self.view.figure.marks = marks

        # self.image.x = self.layer.data[self._viewer_state.x_att]
        # self.image.y = self.layer.data[self._viewer_state.y_att]
        # if hasattr(self.layer, 'to_mask'):  # TODO: what is the best way to test if it is Data or Subset?
        #     self.image.selected = np.nonzero(self.layer.to_mask())[0].tolist()
        #     self.image.selected_style = {}
        #     self.image.unselected_style = {'fill': 'none', 'stroke': 'none'}
        # else:
        #     self.image.selected = []
        #     self.image.selected_style = {}
        #     self.image.unselected_style = {}
        #     #self.image.selected_style = {'fill': 'none', 'stroke': 'none'}
        #     #self.image.unselected_style = {'fill': 'green', 'stroke': 'none'}


