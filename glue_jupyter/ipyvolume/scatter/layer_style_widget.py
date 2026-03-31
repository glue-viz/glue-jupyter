import traitlets
import ipyvuetify as v
from ipywidgets import DOMWidget, widget_serialization
from echo.vue import autoconnect_callbacks_to_vue

from glue_jupyter.widgets import Color, Size


__all__ = ['Scatter3DLayerStateWidget']


class Scatter3DLayerStateWidget(v.VuetifyTemplate):

    template_file = (__file__, 'layer_style_widget.vue')

    widget_size = traitlets.Instance(DOMWidget, allow_none=True).tag(sync=True, **widget_serialization)
    widget_color = traitlets.Instance(DOMWidget, allow_none=True).tag(sync=True, **widget_serialization)

    def __init__(self, layer_state):
        super().__init__()

        self.state = layer_state

        self.widget_size = Size(state=self.state)
        self.widget_color = Color(state=self.state)

        autoconnect_callbacks_to_vue(layer_state, self)
