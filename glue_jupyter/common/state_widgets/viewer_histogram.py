import ipyvuetify as v

from ...widgets.linked_dropdown import LinkedDropdownVuetify
from .vuetify_helpers import link_vuetify_checkbox, link_vuetify_generic

__all__ = ['HistogramViewerStateWidget']


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
                                                     function_to_state=lambda x: x == 0,
                                                     function_to_widget=lambda x: 0 if x else None)

        self.button_cumulative = v.BtnToggle(children=[v.Btn(small=True, class_='ma-2',
                                                             children=['cumulative'])])
        self._link_cumulative = link_vuetify_generic('change', self.button_cumulative,
                                                     self.state, 'cumulative',
                                                     function_to_state=lambda x: x == 0,
                                                     function_to_widget=lambda x: 0 if x else None)

        self.widget_x_axis = LinkedDropdownVuetify(self.state, 'x_att', label='x axis')

        super().__init__(row=True,
                         children=[self.widget_x_axis,
                                   self.button_normalize,
                                   self.button_cumulative,
                                   self.widget_show_axes])
