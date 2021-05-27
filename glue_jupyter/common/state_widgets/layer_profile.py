from ipyvuetify import VuetifyTemplate
import traitlets
from ...state_traitlets_helpers import GlueState
from ...vuetify_helpers import load_template, link_glue_choices

__all__ = ['ProfileLayerStateWidget']


class ProfileLayerStateWidget(VuetifyTemplate):
    template = load_template('layer_profile.vue', __file__)

    glue_state = GlueState().tag(sync=True)

    attribute_items = traitlets.List().tag(sync=True)
    attribute_selected = traitlets.Int().tag(sync=True)

    def __init__(self, layer_state):
        super().__init__()

        self.glue_state = layer_state

        link_glue_choices(self, layer_state, 'attribute')
