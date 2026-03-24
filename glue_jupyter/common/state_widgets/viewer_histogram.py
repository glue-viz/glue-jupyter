import ipyvuetify as v

from echo.vue import autoconnect_callbacks_to_vue
from echo.vue._connect import connect_bool

__all__ = ['HistogramViewerStateWidget']


class HistogramViewerStateWidget(v.VuetifyTemplate):
    template_file = (__file__, 'viewer_histogram.vue')

    def __init__(self, viewer_state):
        super().__init__()

        self.viewer_state = viewer_state

        autoconnect_callbacks_to_vue(viewer_state, self)

        # Properties only used in JS, not bound to a Vue component
        connect_bool(viewer_state, 'normalize', self)
        connect_bool(viewer_state, 'cumulative', self)

    def vue_bins_to_axis(self, *args):
        self.viewer_state.update_bins_to_view()
