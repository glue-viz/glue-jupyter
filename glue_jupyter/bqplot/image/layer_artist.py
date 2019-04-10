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
from glue_jupyter.compat import LayerArtist

from ...link import link, on_change
from ...widgets import LinkedDropdown

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


BqplotImageLayerArtist = ImageLayerArtist

class BqplotImageLayerArtist(ImageLayerArtist):

    def redraw(self):
        pass
        # self.update()

    def create_widgets(self):
        children = []
        self.widget_visible = widgets.Checkbox(description='visible', value=self.state.visible)
        link((self.state, 'visible'), (self.widget_visible, 'value'))

        self.widget_opacity = widgets.FloatSlider(min=0, max=1, step=0.01, value=self.state.alpha, description='opacity')
        link((self.state, 'alpha'), (self.widget_opacity, 'value'))

        children.extend([self.widget_visible, self.widget_opacity])

        if isinstance(self.layer, Subset):

            self.widget_color = widgets.ColorPicker(description='color')
            # link((self.state, 'color'), (self.widget_color, 'value'))
            # on_change([(self.state, 'color')])(self._update_cmap)
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

            self.widget_percentile = LinkedDropdown(self.state, 'percentile', ui_name='limits', label='percentile')

            # on_change([(self.state, 'bias', 'contrast', 'v_min', 'v_max')])(self._update_scale_image)

            self.state.color = '#aaaaaa'

            self.widget_colormap = widgets.Dropdown(options=colormaps, value=colormaps[0][1], description='colormap')
            # link((self.widget_colormap, 'label'), (self.state, 'cmap'))
            # on_change([(self.state, 'cmap')])(self._update_cmap)
            # self._update_cmap()

            children.extend([self.widget_percentile, self.widget_contrast, self.widget_bias, self.widget_colormap])

        return widgets.VBox(children)
