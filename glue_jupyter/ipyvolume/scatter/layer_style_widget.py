import ipyvuetify as v
from echo.vue import autoconnect_callbacks_to_vue

from ...vuetify_helpers import cmap_extras


__all__ = ['Scatter3DLayerStateWidget']


class Scatter3DLayerStateWidget(v.VuetifyTemplate):

    template_file = (__file__, 'layer_style_widget.vue')

    def __init__(self, layer_state):
        super().__init__()

        self.state = layer_state

        extras = {"cmap": cmap_extras(self)}
        autoconnect_callbacks_to_vue(layer_state, self, extras=extras)
