import ipyvuetify as v
import traitlets

from math import log
from echo.vue import autoconnect_callbacks_to_vue
from ipywidgets import ColorPicker, DOMWidget, widget_serialization

from glue.core.subset import Subset
from glue.utils import color2hex

from glue_jupyter.widgets import Color

from ...link import link

__all__ = ['Volume3DLayerStateWidget']


class Volume3DLayerStateWidget(v.VuetifyTemplate):

    template_file = (__file__, 'layer_style_widget.vue')

    widget_color = traitlets.Instance(DOMWidget, allow_none=True).tag(sync=True, **widget_serialization)

    def __init__(self, layer_state):
        super().__init__()

        self.state = layer_state

        if self.state.vmin is None:
            self.state.vmin = 0

        if self.state.vmax is None:
            self.state.vmax = 1

        if isinstance(layer_state.layer, Subset):
            self.widget_color = ColorPicker(value=color2hex(self.state.color), description='color')
            link((self.state, 'color'), (self.widget_color, 'value'), color2hex)
        else:
            self.widget_color = Color(state=self.state, cmap_mode_attr='color_mode', cmap_att=None)

        extras = {"opacity_scale": ("float", self._value_to_exponent, self._exponent_to_value)}
        autoconnect_callbacks_to_vue(layer_state, self, extras=extras)

    def _exponent_to_value(self, exponent, base=10):
        return base ** exponent

    def _value_to_exponent(self, value, base=10):
        return log(value, base)
