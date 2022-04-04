import ipyvuetify as v
from ..state_traitlets_helpers import GlueState

__all__ = ['AxesLimits']


class AxesLimits(v.VuetifyTemplate):
    template_file = (__file__, 'axes_limits.vue')

    glue_state = GlueState().tag(sync=True)

    def __init__(self, viewer_state):
        super().__init__()
        self.glue_state = viewer_state
