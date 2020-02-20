from ipywidgets import Checkbox, VBox, ToggleButtons
from glue_jupyter.widgets import Color, Size

from ...link import link, dlink
from ...widgets import LinkedDropdown

__all__ = ['Scatter3DLayerStateWidget']


class Scatter3DLayerStateWidget(VBox):

    def __init__(self, layer_state):

        self.state = layer_state

        self.widget_visible = Checkbox(description='visible', value=self.state.visible)
        link((self.state, 'visible'), (self.widget_visible, 'value'))

        self.widget_marker = ToggleButtons(options=['sphere', 'box', 'diamond', 'circle_2d'])
        link((self.state, 'geo'), (self.widget_marker, 'value'))

        self.widget_size = Size(state=self.state)
        self.widget_color = Color(state=self.state)

        # vector/quivers
        self.widget_vector = Checkbox(description='show vectors', value=self.state.vector_visible)

        self.widget_vector_x = LinkedDropdown(self.state, 'vx_att', label='vx')
        self.widget_vector_y = LinkedDropdown(self.state, 'vy_att', label='vy')
        self.widget_vector_z = LinkedDropdown(self.state, 'vz_att', label='vz')

        link((self.state, 'vector_visible'), (self.widget_vector, 'value'))
        dlink((self.widget_vector, 'value'), (self.widget_vector_x.layout, 'display'),
              lambda value: None if value else 'none')
        dlink((self.widget_vector, 'value'), (self.widget_vector_y.layout, 'display'),
              lambda value: None if value else 'none')
        dlink((self.widget_vector, 'value'), (self.widget_vector_z.layout, 'display'),
              lambda value: None if value else 'none')

        link((self.state, 'vector_visible'), (self.widget_vector, 'value'))

        super().__init__([self.widget_visible, self.widget_marker,
                         self.widget_size, self.widget_color,
                         self.widget_vector, self.widget_vector_x,
                         self.widget_vector_y, self.widget_vector_z])
