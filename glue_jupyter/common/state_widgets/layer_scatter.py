import ipyvuetify as v
import traitlets

from glue.config import colormaps

from echo.vue import autoconnect_callbacks_to_vue

from ...vuetify_helpers import link_glue

__all__ = ["ScatterLayerStateWidget"]


class ScatterLayerStateWidget(v.VuetifyTemplate):

    template_file = (__file__, "layer_scatter.vue")

    cmap_items = traitlets.List().tag(sync=True)
    cmap_name = traitlets.Unicode().tag(sync=True)

    dpi = traitlets.Float().tag(sync=True)

    def __init__(self, layer_state):
        super().__init__()

        self.layer_state = layer_state

        autoconnect_callbacks_to_vue(layer_state, self,
                                     extras={'density_map': 'bool'})

        self.cmap_items = [
            {"text": cmap[0], "value": cmap[1].name} for cmap in colormaps.members
        ]

        # Sync colormap name (Colormap objects can't be serialized directly)
        def _sync_cmap_name(*args):
            self.cmap_name = layer_state.cmap.name if layer_state.cmap is not None else ''
        layer_state.add_callback('cmap', _sync_cmap_name)
        _sync_cmap_name()

        # dpi comes from the viewer state, not the layer state
        link_glue(self, "dpi", layer_state.viewer_state)

    def vue_set_colormap(self, data):
        cmap = None
        for member in colormaps.members:
            if member[1].name == data:
                cmap = member[1]
                break
        self.layer_state.cmap = cmap
