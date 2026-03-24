import ipyvuetify as v
import traitlets

from echo.vue import autoconnect_callbacks_to_vue

from ...vuetify_helpers import cmap_extras, link_glue

__all__ = ["ScatterLayerStateWidget"]


class ScatterLayerStateWidget(v.VuetifyTemplate):

    template_file = (__file__, "layer_scatter.vue")

    dpi = traitlets.Float().tag(sync=True)

    def __init__(self, layer_state):
        super().__init__()

        self.layer_state = layer_state

        autoconnect_callbacks_to_vue(layer_state, self,
                                     extras={'density_map': 'bool',
                                             'cmap': cmap_extras(self)})

        # dpi comes from the viewer state, not the layer state
        link_glue(self, "dpi", layer_state.viewer_state)
