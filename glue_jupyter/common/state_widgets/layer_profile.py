from ipyvuetify import VuetifyTemplate
import traitlets
from ...state_traitlets_helpers import GlueState
from ...vuetify_helpers import link_glue_choices, link_glue

__all__ = ['ProfileLayerStateWidget']


class ProfileLayerStateWidget(VuetifyTemplate):
    template_file = (__file__, 'layer_profile.vue')

    glue_state = GlueState().tag(sync=True)

    attribute_items = traitlets.List().tag(sync=True)
    attribute_selected = traitlets.Int().tag(sync=True)
    as_steps = traitlets.Bool(False).tag(sync=True)

    def __init__(self, layer_state):
        super().__init__()

        self.glue_state = layer_state

        link_glue_choices(self, layer_state, 'attribute')
        link_glue(self, 'as_steps', layer_state)
