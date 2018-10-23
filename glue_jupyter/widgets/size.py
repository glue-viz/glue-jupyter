import traitlets
import ipywidgets as widgets

from glue.config import colormaps

from ..link import link, dlink, calculation, link_component_id_to_select_widget, on_change

class Size(widgets.VBox):

    def __init__(self, state, **kwargs):
        super(Size, self).__init__(**kwargs)
        self.state = state

        self.widget_size = widgets.FloatSlider(description='size', min=0, max=10, value=self.state.size)
        link((self.state, 'size'), (self.widget_size, 'value'))
        self.widget_scaling = widgets.FloatSlider(description='scale', min=0, max=2, value=self.state.size_scaling)
        link((self.state, 'size_scaling'), (self.widget_scaling, 'value'))


        options = type(self.state).size_mode.get_choice_labels(self.state)
        self.widget_size_mode = widgets.RadioButtons(options=options, description='size mode')
        link((self.state, 'size_mode'), (self.widget_size_mode, 'value'))

        helper = self.state.size_att_helper
        self.widget_size_att = widgets.Dropdown(options=[k.label for k in helper.choices],
                                       value=self.state.size_att, description='size')
        link_component_id_to_select_widget(self.state, 'size_att', self.widget_size_att)


        self.widget_size_vmin = widgets.FloatText(description='size min')
        self.widget_size_vmax = widgets.FloatText(description='size min')
        self.widget_size_v = widgets.VBox([self.widget_size_vmin, self.widget_size_vmax])
        link((self.state, 'size_vmin'), (self.widget_size_vmin, 'value'))
        link((self.state, 'size_vmax'), (self.widget_size_vmax, 'value'))

        dlink((self.widget_size_mode, 'value'), (self.widget_size.layout, 'display'),     lambda value: None if value == options[0] else 'none')
        dlink((self.widget_size_mode, 'value'), (self.widget_size_att.layout, 'display'), lambda value: None if value == options[1] else 'none')
        dlink((self.widget_size_mode, 'value'), (self.widget_size_v.layout, 'display'), lambda value: None if value == options[1] else 'none')

        self.children = (self.widget_size_mode, self.widget_size, self.widget_scaling, self.widget_size_att, self.widget_size_v)