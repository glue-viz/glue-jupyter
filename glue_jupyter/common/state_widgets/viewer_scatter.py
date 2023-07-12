import ipyvuetify as v
import traitlets

from ...state_traitlets_helpers import GlueState
from ...vuetify_helpers import link_glue_choices

__all__ = ["ScatterViewerStateWidget"]


class ScatterViewerStateWidget(v.VuetifyTemplate):

    template_file = (__file__, "viewer_scatter.vue")

    glue_state = GlueState().tag(sync=True)

    x_att_items = traitlets.List().tag(sync=True)
    x_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    y_att_items = traitlets.List().tag(sync=True)
    y_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    def __init__(self, viewer_state):

        super().__init__()

        self.viewer_state = viewer_state
        self.glue_state = viewer_state

        link_glue_choices(self, viewer_state, "x_att")
        link_glue_choices(self, viewer_state, "y_att")
