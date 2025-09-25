import traitlets
import ipyvuetify as v
from echo import delay_callback
from ..link import dlink
from ..state_traitlets_helpers import GlueState

__all__ = ['AxesLimits']


class AxesLimits(v.VuetifyTemplate):
    template_file = (__file__, 'axes_limits.vue')

    glue_state = GlueState().tag(sync=True)

    x_min = traitlets.Float(default_value=None, allow_none=True).tag(sync=True)
    x_max = traitlets.Float(default_value=None, allow_none=True).tag(sync=True)
    y_min = traitlets.Float(default_value=None, allow_none=True).tag(sync=True)
    y_max = traitlets.Float(default_value=None, allow_none=True).tag(sync=True)

    def __init__(self, viewer_state):
        super().__init__()
        self.glue_state = viewer_state
        dlink((self.glue_state, 'x_min'), (self, 'x_min'))
        dlink((self.glue_state, 'x_max'), (self, 'x_max'))
        dlink((self.glue_state, 'y_min'), (self, 'y_min'))
        dlink((self.glue_state, 'y_max'), (self, 'y_max'))

    def vue_apply_limits(self, data):
        self._cache = (self.x_min, self.x_max, self.y_min, self.y_max)
        with delay_callback(self.glue_state, 'x_min', 'x_max', 'y_min', 'y_max'):
            if self.x_min is not None:
                self.glue_state.x_min = self.x_min
            if self.x_max is not None:
                self.glue_state.x_max = self.x_max
            if self.y_min is not None:
                self.glue_state.y_min = self.y_min
            if self.y_max is not None:
                self.glue_state.y_max = self.y_max
