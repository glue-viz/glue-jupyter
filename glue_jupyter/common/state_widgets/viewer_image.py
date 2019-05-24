from ipywidgets import VBox, Checkbox

from ...link import link
from ...widgets.linked_dropdown import LinkedDropdown
from ...common.slice_helpers import MultiSliceWidgetHelper

__all__ = ['ImageViewerStateWidget']


class ImageViewerStateWidget(VBox):

    def __init__(self, viewer_state):

        self.state = viewer_state

        # Set checkbox for showing/hiding axes

        self.widget_show_axes = Checkbox(value=True, description="Show axes")
        link((self.widget_show_axes, 'value'), (self.state, 'show_axes'))

        # Set up dropdown for color mode

        self.widget_color_mode = LinkedDropdown(self.state, 'color_mode', label='mode')

        # Set up checkbox for aspect ratio

        self.widgets_aspect = Checkbox(description='Equal aspect ratio')
        aspect_mapping = {'equal': True, 'auto': False}
        aspect_mapping_inverse = {True: 'equal', False: 'auto'}
        link((self.state, 'aspect'), (self.widgets_aspect, 'value'),
             lambda x: aspect_mapping[x], lambda x: aspect_mapping_inverse[x])

        # Set up dropdown for reference data

        self.widget_reference_data = LinkedDropdown(self.state, 'reference_data', label='reference')

        # Set up dropdowns for main attributes

        self.widget_axis_x = LinkedDropdown(self.state, 'x_att_world', label='x axis')
        self.widget_axis_y = LinkedDropdown(self.state, 'y_att_world', label='y axis')

        # Set up sliders for remaining dimensions

        self.sliders = VBox()
        self.sliders_helper = MultiSliceWidgetHelper(self.state, self.sliders)

        super().__init__([self.widget_color_mode, self.widget_reference_data,
                          self.widgets_aspect, self.widget_axis_x,
                          self.widget_axis_y, self.sliders, self.widget_show_axes])
