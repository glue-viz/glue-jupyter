import ipyvuetify as v

from echo.vue import autoconnect_callbacks_to_vue

from ...vuetify_helpers import cmap_extras

__all__ = ["ScatterLayerStateWidget"]


class ScatterLayerStateWidget(v.VuetifyTemplate):

    template_file = (__file__, "layer_scatter.vue")

    def __init__(self, layer_state):
        super().__init__()

        self.layer_state = layer_state

        autoconnect_callbacks_to_vue(layer_state, self,
                                     extras={'density_map': 'bool',
                                             'cmap': cmap_extras(self)},
                                     skip={'dpi'})

        autoconnect_callbacks_to_vue(layer_state.viewer_state, self,
                                     only={'dpi': 'number'})
