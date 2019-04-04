import numpy as np
import bqplot
from ipyastroimage.astroimage import AstroImage
import ipywidgets as widgets
import ipywidgets.widgets.trait_types as tt
import matplotlib.cm

from glue.core.exceptions import IncompatibleAttribute
from glue.core.data import Subset
from glue.viewers.image.state import ImageLayerState
from glue.viewers.image.layer_artist import ImageLayerArtist
from glue.viewers.common.layer_artist import LayerArtist

from ...link import link, on_change

# FIXME: monkey patch ipywidget to accept anything
tt.Color.validate = lambda self, obj, value: value


colormaps = [('Viridis', 'viridis'), ('Jet', 'jet'), ('Grey', ['black', 'grey']), ('RdYlGn', 'RdYlGn')]

def _mask_to_rgba_data(mask, color):
    r, g, b = matplotlib.colors.to_rgb(color)
    rgba = np.zeros(mask.shape + (4,), dtype=np.uint8)
    rgba[mask.astype(np.bool),3] = 0.5 * 255
    rgba[...,0:3] = r * 255, g * 255, b * 255
    rgba[mask,3] = 255
    rgba[~mask,3] = 0
    return rgba


class BqplotImageLayerArtist(LayerArtist):
    _layer_state_cls = ImageLayerState

    get_layer_color = ImageLayerArtist.get_layer_color
    get_image_shape = ImageLayerArtist.get_image_shape
    get_image_data  = ImageLayerArtist.get_image_data
    _update_visual_attributes = ImageLayerArtist._update_visual_attributes
    #_update_compatibility = ImageLayerArtist._update_compatibility

    def __init__(self, view, viewer_state, layer_state=None, layer=None):

        super(BqplotImageLayerArtist, self).__init__(viewer_state,
                                                     layer_state=layer_state, layer=layer)

        self.view = view

        # self._update_compatibility()

        self.scale_image = bqplot.ColorScale()
        self.scales = {'x': self.view.scale_x, 'y': self.view.scale_y, 'image': self.scale_image}
        self.image_mark = AstroImage(image=[[1, 2], [3,4]], scales=self.scales)
        self.color_axis = bqplot.ColorAxis(side='right', scale=self.scale_image, orientation='vertical')
        self.view.figure.axes = list(self.view.figure.axes) + [self.color_axis]

        self.view.figure.marks = list(self.view.figure.marks) + [self.image_mark]

        viewer_state.add_callback('x_att', self._update_xy_att)
        viewer_state.add_callback('y_att', self._update_xy_att)

    def _update_xy_att(self, *args):
        self.update()

    def redraw(self):
        self.update()

    def _workaround_unselected_style(self, change):
        # see https://github.com/bloomberg/bqplot/issues/606
        if hasattr(self.layer, 'to_mask'):  # TODO: what is the best way to test if it is Data or Subset?
            self.image.unselected_style = {'fill': 'white', 'stroke': 'none'}
            self.image.unselected_style = {'fill': 'none', 'stroke': 'none'}

    def _update_scale_image(self):
        contrast = self.state.contrast
        bias = self.state.bias
        if not isinstance(self.layer, Subset):
            min = self.state.v_min
            max = self.state.v_max
            width = max - min
            mid = (min + max) / 2.
            min = (min - bias * width)*contrast + 0.5 * width
            max = (max - bias * width)*contrast + 0.5 * width
            with self.scale_image.hold_sync():
                self.scale_image.min = min
                self.scale_image.max = max

    def _update_cmap(self):
        if isinstance(self.layer, Subset):
            self.scale_image.colors = ['white', self.state.color]
        else:
            name = self.state.cmap
            value = dict(colormaps)[name]
            if isinstance(value, list):
                self.scale_image.colors = value
            else:
                # with self.scale_image.hold_sync():
                self.scale_image.colors = []
                self.scale_image.scheme = value



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
            #data = self.layer.data[self.state.attribute].astype(np.float32)
            data = mask.astype(np.float32)
            data[~mask] = np.nan
            self.image_mark.image = data
        else:
            data = self.layer[self.state.attribute]
            # data = data - self.state.v_min
            # data /= (self.state.v_max - self.state.v_min)
            # print(np.nanmin(data), np.nanmax(data))
            # png_data = _scalar_to_png_data(data)
            self.scale_image.min = self.state.v_min
            self.scale_image.max = self.state.v_max
            self.image_mark.image = data
        # force the image mark to update the image data
        # self.image_mark.send_state(key='image')
        height, width = data.shape
        self.image_mark.x = [0, width]
        self.image_mark.y = [0, height]
        # bug? this will cause a redraw for sure, but why is this needed?
        marks = list(self.view.figure.marks)
        self.view.figure.marks = []
        self.view.figure.marks = marks

    def create_widgets(self):
        children = []
        self.widget_visible = widgets.Checkbox(description='visible', value=self.state.visible)
        link((self.state, 'visible'), (self.widget_visible, 'value'))
        link((self.state, 'visible'), (self.image_mark, 'visible'))

        self.widget_opacity = widgets.FloatSlider(min=0, max=1, step=0.01, value=self.state.alpha, description='opacity')
        link((self.state, 'alpha'), (self.widget_opacity, 'value'))
        link((self.state, 'alpha'), (self.image_mark, 'opacity'))

        children.extend([self.widget_visible, self.widget_opacity])

        if isinstance(self.layer, Subset):
            self.widget_color = widgets.ColorPicker(description='color')
            link((self.state, 'color'), (self.widget_color, 'value'))
            on_change([(self.state, 'color')])(self._update_cmap)
            children.extend([self.widget_color])
        else:
            self.widget_contrast = widgets.FloatSlider(min=0, max=4, step=0.01, value=self.state.contrast, description='contrast')
            link((self.state, 'contrast'), (self.widget_contrast, 'value'))

            self.widget_bias = widgets.FloatSlider(min=0, max=1, step=0.01, value=self.state.bias, description='bias')
            link((self.state, 'bias'), (self.widget_bias, 'value'))

            # TODO: refactor: this is a copy from state
            percentile_display = {100: 'Min/Max',
                          99.5: '99.5%',
                          99: '99%',
                          95: '95%',
                          90: '90%'}
                          #'Custom': 'Custom'} # TODO: support custom

            self.widget_percentile = widgets.Dropdown(options=[(percentile_display[k], k) for k in [100, 99.5, 99, 95, 90]],#, 'Custom']],
                                           value=self.state.percentile, description='limits')
            link((self.state, 'percentile'), (self.widget_percentile, 'value'))
            on_change([(self.state, 'bias', 'contrast', 'v_min', 'v_max')])(self._update_scale_image)

            self.widget_colormap = widgets.Dropdown(options=colormaps, value=colormaps[0][1], description='colormap')
            link((self.widget_colormap, 'label'), (self.state, 'cmap'))
            on_change([(self.state, 'cmap')])(self._update_cmap)
            self._update_cmap()

            children.extend([self.widget_percentile, self.widget_contrast, self.widget_bias, self.widget_colormap])

        return widgets.VBox(children)
