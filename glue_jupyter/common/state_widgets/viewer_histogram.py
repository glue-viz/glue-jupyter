import ipyvuetify as v

from echo.vue import autoconnect_callbacks_to_vue

__all__ = ['HistogramViewerStateWidget']


class HistogramViewerStateWidget(v.VuetifyTemplate):
    template_file = (__file__, 'viewer_histogram.vue')

    def __init__(self, viewer_state):
        super().__init__()

        self.viewer_state = viewer_state

        autoconnect_callbacks_to_vue(viewer_state, self,
                                     extras={'normalize': 'bool',
                                             'cumulative': 'bool'})

    def vue_bins_to_axis(self, *args):
        self.viewer_state.update_bins_to_view()
