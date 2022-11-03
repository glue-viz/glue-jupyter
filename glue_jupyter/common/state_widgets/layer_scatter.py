from ipywidgets import Checkbox, FloatSlider, VBox, IntSlider, IntText
from glue_jupyter.widgets import Color, Size

from ...link import link, dlink
from ...widgets import LinkedDropdown

__all__ = ['ScatterLayerStateWidget']


class ScatterLayerStateWidget(VBox):

    def __init__(self, layer_state):

        self.state = layer_state

        self.widget_visible = Checkbox(description='visible', value=self.state.visible)
        link((self.state, 'visible'), (self.widget_visible, 'value'))

        self.widget_fill = Checkbox(description='fill', value=self.state.fill)
        link((self.state, 'fill'), (self.widget_fill, 'value'))

        self.widget_opacity = FloatSlider(min=0, max=1, step=0.01, value=self.state.alpha,
                                          description='opacity')
        link((self.state, 'alpha'), (self.widget_opacity, 'value'))

        self.widget_color = Color(state=self.state)
        self.widget_size = Size(state=self.state)

        self.widget_vector = Checkbox(description='show vectors', value=self.state.vector_visible)
        link((self.state, 'vector_visible'), (self.widget_vector, 'value'))

        self.widget_vector_x = LinkedDropdown(self.state, 'vx_att', ui_name='vx',
                                              label='vx attribute')
        self.widget_vector_y = LinkedDropdown(self.state, 'vy_att', ui_name='vy',
                                              label='vy attribute')

        self.widget_zorder = IntText(description='z-order')
        link((self.state, 'zorder'), (self.widget_zorder, 'value'))

        dlink((self.widget_vector, 'value'), (self.widget_vector_x.layout, 'display'),
              lambda value: None if value else 'none')
        dlink((self.widget_vector, 'value'), (self.widget_vector_y.layout, 'display'),
              lambda value: None if value else 'none')

        # TODO: the following shouldn't be necessary ideally
        if hasattr(self.state, 'bins'):
            self.widget_bins = IntSlider(min=0, max=1024, value=self.state.bins,
                                         description='bin count')
            link((self.state, 'bins'), (self.widget_bins, 'value'))

        super().__init__([self.widget_visible, self.widget_fill, self.widget_opacity,
                          self.widget_size, self.widget_color,
                          self.widget_vector, self.widget_vector_x,
                          self.widget_vector_y, self.widget_zorder])
