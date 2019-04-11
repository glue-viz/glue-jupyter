from ipywidgets import Checkbox, FloatSlider, VBox, IntSlider
from glue_jupyter.widgets import Color, Size

from ...link import link, dlink
from ...widgets import LinkedDropdown

__all__ = ['ScatterLayerStateWidget']


class ScatterLayerStateWidget(VBox):

    def __init__(self, layer_state):

        self.state = layer_state

        # NOTE: we need to use backwards=False here to make sure that changing
        # state.vector_visible doesn't cause self.state.visible to change
        # via self.widget_visible.value
        self.widget_visible = Checkbox(description='visible', value=self.state.visible)
        link((self.state, 'visible'), (self.widget_visible, 'value'), backwards=False)

        print(self.state.visible)
        print(self.widget_visible.value)

        self.widget_opacity = FloatSlider(min=0, max=1, step=0.01, value=self.state.alpha, description='opacity')
        link((self.state, 'alpha'), (self.widget_opacity, 'value'))

        self.widget_color = Color(state=self.state)
        self.widget_size = Size(state=self.state)

        self.widget_vector = Checkbox(description='show vectors', value=self.state.vector_visible)
        link((self.state, 'vector_visible'), (self.widget_vector, 'value'), backwards=False)

        self.widget_vector_x = LinkedDropdown(self.state, 'vx_att', ui_name='vx', label='vx attribute')
        self.widget_vector_y = LinkedDropdown(self.state, 'vy_att', ui_name='vy', label='vy attribute')

        dlink((self.widget_vector, 'value'), (self.widget_vector_x.layout, 'display'), lambda value: None if value else 'none')
        dlink((self.widget_vector, 'value'), (self.widget_vector_y.layout, 'display'), lambda value: None if value else 'none')

        self.widget_bins = IntSlider(min=0, max=1024, value=self.state.bins, description='bin count')
        link((self.state, 'bins'), (self.widget_bins, 'value'))

        super().__init__([self.widget_visible, self.widget_opacity,
                          self.widget_size, self.widget_color,
                          self.widget_vector, self.widget_vector_x,
                          self.widget_vector_y])
