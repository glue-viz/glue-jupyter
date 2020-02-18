import ipyvuetify as v

from .vuetify_helpers import link_vuetify_checkbox, link_vuetify_generic

from glue.utils import color2hex

from ...link import link

__all__ = ['HistogramLayerStateWidget']


class HistogramLayerStateWidget(v.Container):

    def __init__(self, layer_state):

        self.state = layer_state

        self.widget_visible = v.Checkbox(label='Visible', v_model=True)
        self._link_visible = link_vuetify_checkbox(self.widget_visible,  self.state, 'visible')

        self.widget_color = v.ColorPicker(flat=True)
        self._link_color = link_vuetify_generic('update:color', self.widget_color,  self.state, 'color', function_to_widget=color2hex)

        super().__init__(row=True,
                         children=[self.widget_visible, self.widget_color])

    def cleanup(self):
        self._link_visible.disconnect()
        self._link_color.disconnect()
