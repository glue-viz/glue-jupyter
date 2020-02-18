import ipyvuetify as v

from ...widgets.linked_dropdown import LinkedDropdownVuetify
from .vuetify_helpers import link_vuetify_checkbox, link_vuetify_button

__all__ = ['HistogramViewerStateWidget']


class HistogramViewerStateWidget(v.Container):

    def __init__(self, viewer_state):

        self.state = viewer_state

        self.widget_show_axes = v.Checkbox(label='Show axes', v_model=True)
        self._link_checkbox = link_vuetify_checkbox(self.widget_show_axes,  self.state, 'show_axes')

        self.button_normalize = v.Btn(color='primary', small=True, class_='ma-0',
                                      children=['normalize'], v_model=True)
        self._link_normalize = link_vuetify_button(self.button_normalize,  self.state, 'normalize')

        self.button_cumulative = v.Btn(color='primary', small=True, class_='ma-0',
                                       children=['cumulative'], v_model=True)
        self._link_cumulative = link_vuetify_button(self.button_cumulative,  self.state, 'cumulative')

        self.widget_x_axis = LinkedDropdownVuetify(self.state, 'x_att', label='x axis')

        toggle_v_model = []
        if not self.state.normalize:
            toggle_v_model.append(0)
        if not self.state.cumulative:
            toggle_v_model.append(1)

        super().__init__(row=True,
                         children=[self.widget_x_axis,
                                   v.BtnToggle(multiple=True,
                                               v_model=toggle_v_model,
                                               children=[self.button_normalize,
                                                         self.button_cumulative]),
                                   self.widget_show_axes])
