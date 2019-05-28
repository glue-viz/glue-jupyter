from ipywidgets import Checkbox, ColorPicker, VBox, IntText, FloatText

from glue.utils import color2hex

from ...widgets import LinkedDropdown
from ...link import link

__all__ = ['ProfileLayerStateWidget']


class ProfileLayerStateWidget(VBox):

    def __init__(self, layer_state):

        self.state = layer_state

        self.widget_visible = Checkbox(description='visible', value=self.state.visible)
        link((self.state, 'visible'), (self.widget_visible, 'value'))

        self.widget_color = ColorPicker(description='color')
        link((self.state, 'color'), (self.widget_color, 'value'), color2hex)

        self.widget_linewidth = IntText(description='line width')
        link((self.state, 'linewidth'), (self.widget_linewidth, 'value'))

        self.widget_attribute = LinkedDropdown(self.state, 'attribute', label='attribute')

        if self.state.v_min is None:
            self.state.v_min = 0

        self.widget_v_min = FloatText(description='vmin')
        link((self.state, 'v_min'), (self.widget_v_min, 'value'))

        if self.state.v_max is None:
            self.state.v_max = 1

        self.widget_v_max = FloatText(description='vmax')
        link((self.state, 'v_max'), (self.widget_v_max, 'value'))

        self.widget_percentile = LinkedDropdown(self.state, 'percentile', label='percentile')

        super().__init__([self.widget_visible, self.widget_color,
                          self.widget_linewidth, self.widget_attribute,
                          self.widget_v_min, self.widget_v_max,
                          self.widget_percentile])
