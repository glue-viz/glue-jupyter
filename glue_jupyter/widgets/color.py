import traitlets
import ipywidgets as widgets

from glue.config import colormaps

from ..link import link, dlink, calculation, link_component_id_to_select_widget, on_change
import glue_jupyter.widgets


class Color(widgets.VBox):

    def __init__(self, state, **kwargs):
        super(Color, self).__init__(**kwargs)
        self.state = state

        self.widget_color = widgets.ColorPicker(description='color')
        link((self.state, 'color'), (self.widget_color, 'value'))

        cmap_mode_options = type(self.state).cmap_mode.get_choice_labels(self.state)
        self.widget_cmap_mode = widgets.RadioButtons(options=cmap_mode_options, description='cmap mode')
        link((self.state, 'cmap_mode'), (self.widget_cmap_mode, 'value'))

        self.widget_cmap_att = glue_jupyter.widgets.Component(self.state, 'cmap_att', ui_name='color attribute')

        self.widget_cmap_vmin = widgets.FloatText(description='color min')
        self.widget_cmap_vmax = widgets.FloatText(description='color max')
        self.widget_cmap_v = widgets.VBox([self.widget_cmap_vmin, self.widget_cmap_vmax])
        link((self.state, 'cmap_vmin'), (self.widget_cmap_vmin, 'value'))
        link((self.state, 'cmap_vmax'), (self.widget_cmap_vmax, 'value'))

        self.widget_cmap = widgets.Dropdown(options=colormaps, description='colormap')
        link((self.state, 'cmap'), (self.widget_cmap, 'label'), lambda cmap: colormaps.name_from_cmap(cmap), lambda name: colormaps[name])

        dlink((self.widget_cmap_mode, 'value'), (self.widget_color.layout, 'display'),     lambda value: None if value == cmap_mode_options[0] else 'none')
        dlink((self.widget_cmap_mode, 'value'), (self.widget_cmap.layout, 'display'),     lambda value: None if value == cmap_mode_options[1] else 'none')
        dlink((self.widget_cmap_mode, 'value'), (self.widget_cmap_att.layout, 'display'), lambda value: None if value == cmap_mode_options[1] else 'none')
        dlink((self.widget_cmap_mode, 'value'), (self.widget_cmap_v.layout, 'display'), lambda value: None if value == cmap_mode_options[1] else 'none')
        self.children = (self.widget_cmap_mode, self.widget_color, self.widget_cmap_att, self.widget_cmap_v, self.widget_cmap)