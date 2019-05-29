from ipywidgets import Checkbox, ColorPicker, VBox

from glue.utils import color2hex

from ...link import link

__all__ = ['HistogramLayerStateWidget']


class HistogramLayerStateWidget(VBox):

    def __init__(self, layer_state):

        self.state = layer_state

        self.widget_visible = Checkbox(description='visible', value=self.state.visible)
        link((self.state, 'visible'), (self.widget_visible, 'value'))

        self.widget_color = ColorPicker(description='color')
        link((self.state, 'color'), (self.widget_color, 'value'), color2hex)

        super().__init__([self.widget_visible, self.widget_color])
