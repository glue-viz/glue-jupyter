import ipywidgets as widgets

from glue.config import colormaps
from glue.utils import color2hex

from ..link import link, dlink
from .linked_dropdown import LinkedDropdown


class Color(widgets.VBox):

    def __init__(self, state, **kwargs):
        super(Color, self).__init__(**kwargs)
        self.state = state

        self.cmap_att = kwargs.get('cmap_att', 'cmap_att')
        self.color_mode_attr = kwargs.get('color_mode_attr', 'color_mode')

        self.widget_color = widgets.ColorPicker(description='color')
        link((self.state, 'color'), (self.widget_color, 'value'), color2hex)

        color_mode_options = getattr(type(self.state),
                                    self.color_mode_attr).get_choice_labels(self.state)
        self.widget_color_mode = widgets.RadioButtons(options=color_mode_options,
                                                     description='cmap mode')
        link((self.state, self.color_mode_attr), (self.widget_color_mode, 'value'))

        children = [self.widget_color_mode, self.widget_color]
        if self.cmap_att is not None:
            self.widget_cmap_att = LinkedDropdown(self.state, 'cmap_att',
                                                  ui_name='color attribute',
                                                  label='color attribute')
            self.widget_cmap_vmin = widgets.FloatText(description='color min')
            self.widget_cmap_vmax = widgets.FloatText(description='color max')
            self.widget_cmap_v = widgets.VBox([self.widget_cmap_vmin, self.widget_cmap_vmax])
            link((self.state, 'cmap_vmin'),
                 (self.widget_cmap_vmin, 'value'),
                 lambda value: value or 0)
            link((self.state, 'cmap_vmax'),
                 (self.widget_cmap_vmax, 'value'),
                 lambda value: value or 1)
            children.extend((self.widget_cmap_att, self.widget_cmap_v))

        self.widget_cmap = widgets.Dropdown(options=colormaps, description='colormap')
        children.append(self.widget_cmap)
        link((self.state, 'cmap'), (self.widget_cmap, 'label'),
             lambda cmap: colormaps.name_from_cmap(cmap), lambda name: colormaps[name])

        dlink((self.widget_color_mode, 'value'), (self.widget_color.layout, 'display'),
              lambda value: None if value == color_mode_options[0] else 'none')
        dlink((self.widget_color_mode, 'value'), (self.widget_cmap.layout, 'display'),
              lambda value: None if value == color_mode_options[1] else 'none')
        if self.cmap_att is not None:
            dlink((self.widget_color_mode, 'value'), (self.widget_cmap_att.layout, 'display'),
                  lambda value: None if value == color_mode_options[1] else 'none')
            dlink((self.widget_color_mode, 'value'), (self.widget_cmap_v.layout, 'display'),
                  lambda value: None if value == color_mode_options[1] else 'none')
        self.children = tuple(children)
