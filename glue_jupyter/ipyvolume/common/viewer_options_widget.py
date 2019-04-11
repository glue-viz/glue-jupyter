from ipywidgets import Checkbox, VBox

from ...link import link
from ...widgets import LinkedDropdown


__all__ = ['Viewer3DStateWidget']


class Viewer3DStateWidget(VBox):

    def __init__(self, viewer_state):

        self.state = viewer_state

        self.widget_show_axes = Checkbox(value=False, description="Show axes")
        link((self.state, 'visible_axes'), (self.widget_show_axes, 'value'))

        self.widgets_axis = []
        for i, axis_name in enumerate('xyz'):
            widget_axis = LinkedDropdown(self.state, axis_name + '_att', label=axis_name + ' axis')
            self.widgets_axis.append(widget_axis)

        super().__init__([self.widget_show_axes] + self.widgets_axis)
