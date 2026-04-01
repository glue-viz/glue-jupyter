import ipyvuetify as v
import traitlets

from math import log
from echo.vue import autoconnect_callbacks_to_vue

from glue.core.subset import Subset

from ...vuetify_helpers import cmap_extras


__all__ = ['Volume3DLayerStateWidget']


class Volume3DLayerStateWidget(v.VuetifyTemplate):

    is_subset = traitlets.Bool().tag(sync=True)

    template_file = (__file__, 'layer_style_widget.vue')

    def __init__(self, layer_state):
        super().__init__()

        self.state = layer_state

        if self.state.vmin is None:
            self.state.vmin = 0

        if self.state.vmax is None:
            self.state.vmax = 1

        self.is_subset = isinstance(self.state.layer, Subset)

        extras = {
            "opacity_scale": ("float", self._value_to_exponent, self._exponent_to_value),
            "cmap": cmap_extras(self),
        }
        autoconnect_callbacks_to_vue(layer_state, self, extras=extras)

    def _exponent_to_value(self, exponent, base=10):
        return base ** exponent

    def _value_to_exponent(self, value, base=10):
        return log(value, base)
