import ipyvuetify as v
import traitlets
from ...state_traitlets_helpers import GlueState
from ...vuetify_helpers import load_template, link_glue_choices

__all__ = ['HistogramViewerStateWidget']


class HistogramViewerStateWidget(v.VuetifyTemplate):
    template = load_template('viewer_histogram.vue', __file__)
    x_att_items = traitlets.List().tag(sync=True)
    x_att_selected = traitlets.Int(allow_none=True).tag(sync=True)
    glue_state = GlueState().tag(sync=True)

    def __init__(self, viewer_state):
        super().__init__()

        self.glue_state = viewer_state

        link_glue_choices(self, viewer_state, 'x_att')
