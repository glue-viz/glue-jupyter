import ipyvuetify as v

from ...widgets.linked_dropdown import LinkedDropdownVuetify
from .vuetify_helpers import link_vuetify_checkbox, link_vuetify_generic

__all__ = ['HistogramViewerStateWidget']


def model_to_bool(x):
    return x == 0


def bool_to_model(x):
    return 0 if x else None


class HistogramViewerStateWidget(v.Container):

    def __init__(self, viewer_state):

        self.state = viewer_state

        self.widget_show_axes = v.Checkbox(label='Show axes', v_model=True)
        self._link_checkbox = link_vuetify_checkbox(self.widget_show_axes,
                                                    self.state, 'show_axes')

        self.button_normalize = v.BtnToggle(children=[v.Btn(small=True, class_='ma-2',
                                                            children=['normalize'])])
        self._link_cumulative = link_vuetify_generic('change', self.button_normalize,
                                                     self.state, 'normalize',
                                                     function_to_state=model_to_bool,
                                                     function_to_widget=bool_to_model)

        self.button_cumulative = v.BtnToggle(children=[v.Btn(small=True, class_='ma-2',
                                                             children=['cumulative'])])
        self._link_cumulative = link_vuetify_generic('change', self.button_cumulative,
                                                     self.state, 'cumulative',
                                                     function_to_state=model_to_bool,
                                                     function_to_widget=bool_to_model)

        self.widget_x_axis = LinkedDropdownVuetify(self.state, 'x_att', label='x axis')

        super().__init__(row=True,
                         children=[self.widget_x_axis,
                                   self.button_normalize,
                                   self.button_cumulative,
                                   self.widget_show_axes])
