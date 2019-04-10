from glue.viewers.image.state import ImageSubsetLayerState
from ipywidgets import Checkbox, FloatSlider, ColorPicker, VBox, Dropdown, FloatText
import ipywidgets.widgets.trait_types as tt

from ...link import link
from ...widgets import LinkedDropdown

# FIXME: monkey patch ipywidget to accept anything
tt.Color.validate = lambda self, obj, value: value

colormaps = [('Viridis', 'viridis'), ('Jet', 'jet'),
             ('Grey', ['black', 'grey']), ('RdYlGn', 'RdYlGn')]

__all__ = ['ImageLayerStateWidget']


class ImageLayerStateWidget(VBox):

    def __init__(self, layer_state):

        self.state = layer_state

        self.widget_visible = Checkbox(description='visible', value=self.state.visible)
        link((self.state, 'visible'), (self.widget_visible, 'value'))

        self.widget_opacity = FloatSlider(min=0, max=1, step=0.01, value=self.state.alpha, description='opacity')
        link((self.state, 'alpha'), (self.widget_opacity, 'value'))

        self.widget_contrast = FloatSlider(min=0, max=4, step=0.01, value=self.state.contrast, description='contrast')
        link((self.state, 'contrast'), (self.widget_contrast, 'value'))

        self.widget_bias = FloatSlider(min=0, max=1, step=0.01, value=self.state.bias, description='bias')
        link((self.state, 'bias'), (self.widget_bias, 'value'))

        self.widget_percentile = LinkedDropdown(self.state, 'percentile', ui_name='limits', label='percentile')

        self.widget_v_min = FloatText(description='min', value=self.state.v_min)
        link((self.state, 'v_min'), (self.widget_v_min, 'value'))

        self.widget_v_max = FloatText(description='max', value=self.state.v_max)
        link((self.state, 'v_max'), (self.widget_v_max, 'value'))

        self.widget_color = ColorPicker(description='color')
        link((self.state, 'color'), (self.widget_color, 'value'))

        self.widget_colormap = Dropdown(options=colormaps, value=colormaps[0][1], description='colormap')
        link((self.widget_colormap, 'label'), (self.state, 'cmap'))

        super().__init__()

        self.state.viewer_state.add_callback('color_mode', self.setup_widgets)

        self.setup_widgets()

    def setup_widgets(self, *args):

        children = [self.widget_visible, self.widget_opacity]

        if isinstance(self.state, ImageSubsetLayerState):

            children.append(self.widget_color)

        else:

            children.append(self.widget_contrast)
            children.append(self.widget_bias)
            children.append(self.widget_percentile)
            children.append(self.widget_v_min)
            children.append(self.widget_v_max)

            if self.state.viewer_state.color_mode == 'Colormaps':
                children.append(self.widget_colormap)
            else:
                children.append(self.widget_color)

        self.children = children
