import ipywidgets as widgets

from ..link import link, dlink
from .linked_dropdown import LinkedDropdown


class Size(widgets.VBox):

    def __init__(self, state, **kwargs):
        super(Size, self).__init__(**kwargs)
        self.state = state

        self.widget_size = widgets.FloatSlider(description='size', min=0, max=10,
                                               value=self.state.size)
        link((self.state, 'size'), (self.widget_size, 'value'))
        self.widget_scaling = widgets.FloatSlider(description='scale', min=0, max=2,
                                                  value=self.state.size_scaling)
        link((self.state, 'size_scaling'), (self.widget_scaling, 'value'))

        options = type(self.state).size_mode.get_choice_labels(self.state)
        self.widget_size_mode = widgets.RadioButtons(options=options, description='size mode')
        link((self.state, 'size_mode'), (self.widget_size_mode, 'value'))

        self.widget_size_att = LinkedDropdown(self.state, 'size_att',
                                              ui_name='size attribute',
                                              label='size attribute')

        self.widget_size_vmin = widgets.FloatText(description='size min')
        self.widget_size_vmax = widgets.FloatText(description='size min')
        self.widget_size_v = widgets.VBox([self.widget_size_vmin, self.widget_size_vmax])
        link((self.state, 'size_vmin'), (self.widget_size_vmin, 'value'), lambda value: value or 0)
        link((self.state, 'size_vmax'), (self.widget_size_vmax, 'value'), lambda value: value or 1)

        dlink((self.widget_size_mode, 'value'), (self.widget_size.layout, 'display'),
              lambda value: None if value == options[0] else 'none')
        dlink((self.widget_size_mode, 'value'), (self.widget_size_att.layout, 'display'),
              lambda value: None if value == options[1] else 'none')
        dlink((self.widget_size_mode, 'value'), (self.widget_size_v.layout, 'display'),
              lambda value: None if value == options[1] else 'none')

        self.children = (self.widget_size_mode, self.widget_size,
                         self.widget_scaling, self.widget_size_att,
                         self.widget_size_v)
