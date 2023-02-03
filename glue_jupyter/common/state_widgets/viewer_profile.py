import ipyvuetify as v
import traitlets
from ...state_traitlets_helpers import GlueState
from ...vuetify_helpers import link_glue_choices

__all__ = ['ProfileViewerStateWidget']


class ProfileViewerStateWidget(v.VuetifyTemplate):
    template_file = (__file__, 'viewer_profile.vue')

    glue_state = GlueState().tag(sync=True)

    reference_data_items = traitlets.List().tag(sync=True)
    reference_data_selected = traitlets.Int(allow_none=True).tag(sync=True)

    x_att_items = traitlets.List().tag(sync=True)
    x_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    function_items = traitlets.List().tag(sync=True)
    function_selected = traitlets.Int(allow_none=True).tag(sync=True)

    x_display_unit_items = traitlets.List().tag(sync=True)
    x_display_unit_selected = traitlets.Int(allow_none=True).tag(sync=True)

    y_display_unit_items = traitlets.List().tag(sync=True)
    y_display_unit_selected = traitlets.Int(allow_none=True).tag(sync=True)

    def __init__(self, viewer_state):
        super().__init__()

        self.glue_state = viewer_state

        link_glue_choices(self, viewer_state, 'reference_data')
        link_glue_choices(self, viewer_state, 'x_att')
        link_glue_choices(self, viewer_state, 'function')
        link_glue_choices(self, viewer_state, 'x_display_unit')
        link_glue_choices(self, viewer_state, 'y_display_unit')
