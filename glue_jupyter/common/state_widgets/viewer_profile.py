from ipywidgets import VBox, ToggleButton, Checkbox

from ...widgets.linked_dropdown import LinkedDropdown
from ...link import link

__all__ = ['ProfileViewerStateWidget']


class ProfileViewerStateWidget(VBox):

    def __init__(self, viewer_state):

        self.state = viewer_state

        self.widget_show_axes = Checkbox(value=True, description="Show axes")
        link((self.widget_show_axes, 'value'), (self.state, 'show_axes'))

        self.widget_reference_data = LinkedDropdown(self.state, 'reference_data', label='reference')
        self.widget_axis_x = LinkedDropdown(self.state, 'x_att', label='x axis')
        self.widget_function = LinkedDropdown(self.state, 'function', label='function')

        self.button_normalize = ToggleButton(value=False, description='normalize',
                                             tooltip='Normalize profiles')
        link((self.button_normalize, 'value'), (self.state, 'normalize'))

        super().__init__([self.widget_reference_data,
                          self.widget_axis_x, self.widget_function,
                          self.button_normalize, self.widget_show_axes])
