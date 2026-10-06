from ipyvuetify import VuetifyTemplate

from echo.vue import autoconnect_callbacks_to_vue

__all__ = ['LineLayerStateWidget']


class LineLayerStateWidget(VuetifyTemplate):
    template_file = (__file__, 'layer_line.vue')

    def __init__(self, layer_state):
        super().__init__()

        self.layer_state = layer_state

        autoconnect_callbacks_to_vue(layer_state, self)
