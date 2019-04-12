from ipywidgets import VBox

from ...widgets.linked_dropdown import LinkedDropdown

__all__ = ['ScatterViewerStateWidget']


class ScatterViewerStateWidget(VBox):

    def __init__(self, viewer_state):

        self.state = viewer_state

        self.widget_x_axis = LinkedDropdown(self.state, 'x_att', label='x axis')
        self.widget_y_axis = LinkedDropdown(self.state, 'y_att', label='y axis')

        super().__init__([self.widget_x_axis, self.widget_y_axis])
