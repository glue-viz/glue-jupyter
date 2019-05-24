from ipywidgets import VBox, Checkbox

from ...widgets.linked_dropdown import LinkedDropdown
from ...link import link

__all__ = ['ScatterViewerStateWidget']


class ScatterViewerStateWidget(VBox):

    def __init__(self, viewer_state):

        self.state = viewer_state

        self.widget_show_axes = Checkbox(value=True, description="Show axes")
        link((self.widget_show_axes, 'value'), (self.state, 'show_axes'))

        self.widget_x_axis = LinkedDropdown(self.state, 'x_att', label='x axis')
        self.widget_y_axis = LinkedDropdown(self.state, 'y_att', label='y axis')

        super().__init__([self.widget_x_axis, self.widget_y_axis, self.widget_show_axes])
