from ipywidgets import VBox, ToggleButton

from ...widgets.linked_dropdown import LinkedDropdown
from ...link import link

__all__ = ['HistogramViewerStateWidget']


class HistogramViewerStateWidget(VBox):

    def __init__(self, viewer_state):

        self.state = viewer_state

        self.button_normalize = ToggleButton(value=False, description='normalize',
                                             tooltip='Normalize histogram')
        link((self.button_normalize, 'value'), (self.state, 'normalize'))

        self.button_cumulative = ToggleButton(value=False, description='cumulative',
                                             tooltip='Cumulative histogram')
        link((self.button_cumulative, 'value'), (self.state, 'cumulative'))

        self.widget_x_axis = LinkedDropdown(self.state, 'x_att', label='x axis')

        super().__init__([self.widget_x_axis,
                          self.button_normalize, self.button_cumulative])
