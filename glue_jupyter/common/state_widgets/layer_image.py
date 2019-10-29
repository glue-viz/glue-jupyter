from ipywidgets import (Checkbox, FloatSlider, ColorPicker, VBox, Dropdown,
                        FloatText)
from glue.config import colormaps
from glue.utils import color2hex

from ...link import link
from ...widgets import LinkedDropdown

__all__ = ['ImageLayerStateWidget', 'ImageSubsetLayerStateWidget']


class ImageLayerStateWidget(VBox):

    def __init__(self, layer_state):

        self.state = layer_state

        self.widget_visible = Checkbox(description='visible', value=self.state.visible)
        link((self.state, 'visible'), (self.widget_visible, 'value'))

        self.widget_attribute = LinkedDropdown(self.state, 'attribute', label='attribute')

        self.widget_opacity = FloatSlider(min=0, max=1, step=0.01, value=self.state.alpha,
                                          description='opacity')
        link((self.state, 'alpha'), (self.widget_opacity, 'value'))

        self.widget_contrast = FloatSlider(min=0, max=4, step=0.01, value=self.state.contrast,
                                           description='contrast')
        link((self.state, 'contrast'), (self.widget_contrast, 'value'))

        self.widget_bias = FloatSlider(min=0, max=1, step=0.01, value=self.state.bias,
                                       description='bias')
        link((self.state, 'bias'), (self.widget_bias, 'value'))

        self.widget_stretch = LinkedDropdown(self.state, 'stretch', label='stretch')

        self.widget_percentile = LinkedDropdown(self.state, 'percentile', ui_name='limits',
                                                label='percentile')

        self.widget_v_min = FloatText(description='min', value=self.state.v_min)
        link((self.state, 'v_min'), (self.widget_v_min, 'value'))

        self.widget_v_max = FloatText(description='max', value=self.state.v_max)
        link((self.state, 'v_max'), (self.widget_v_max, 'value'))

        self.widget_color = ColorPicker(description='color')
        link((self.state, 'color'), (self.widget_color, 'value'), color2hex)

        self.widget_colormap = Dropdown(options=colormaps.members, description='colormap')
        link((self.state, 'cmap'), (self.widget_colormap, 'value'))

        super().__init__()

        self.state.viewer_state.add_callback('color_mode', self.setup_widgets)

        self.setup_widgets()

    def setup_widgets(self, *args):

        children = [self.widget_visible, self.widget_opacity]

        children.append(self.widget_attribute)
        children.append(self.widget_contrast)
        children.append(self.widget_bias)
        children.append(self.widget_stretch)
        children.append(self.widget_percentile)
        children.append(self.widget_v_min)
        children.append(self.widget_v_max)

        if self.state.viewer_state.color_mode == 'Colormaps':
            children.append(self.widget_colormap)
        else:
            children.append(self.widget_color)

        self.children = children


class ImageSubsetLayerStateWidget(VBox):

    def __init__(self, layer_state):

        self.state = layer_state

        self.widget_visible = Checkbox(description='visible', value=self.state.visible)
        link((self.state, 'visible'), (self.widget_visible, 'value'))

        self.widget_opacity = FloatSlider(min=0, max=1, step=0.01, value=self.state.alpha,
                                          description='opacity')
        link((self.state, 'alpha'), (self.widget_opacity, 'value'))

        self.widget_color = ColorPicker(description='color')
        link((self.state, 'color'), (self.widget_color, 'value'), color2hex)

        super().__init__([self.widget_visible, self.widget_opacity, self.widget_color])
