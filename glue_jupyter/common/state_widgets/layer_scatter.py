import ipyvuetify as v
import traitlets

from glue.config import colormaps

from ...state_traitlets_helpers import GlueState
from ...vuetify_helpers import link_glue, link_glue_choices

__all__ = ["ScatterLayerStateWidget"]


class ScatterLayerStateWidget(v.VuetifyTemplate):

    template_file = (__file__, "layer_scatter.vue")

    glue_state = GlueState().tag(sync=True)

    # Color

    cmap_mode_items = traitlets.List().tag(sync=True)
    cmap_mode_selected = traitlets.Int(allow_none=True).tag(sync=True)

    cmap_att_items = traitlets.List().tag(sync=True)
    cmap_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    cmap_items = traitlets.List().tag(sync=True)

    # Points

    points_mode_items = traitlets.List().tag(sync=True)
    points_mode_selected = traitlets.Int(allow_none=True).tag(sync=True)

    size_mode_items = traitlets.List().tag(sync=True)
    size_mode_selected = traitlets.Int(allow_none=True).tag(sync=True)

    size_att_items = traitlets.List().tag(sync=True)
    size_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    dpi = traitlets.Float().tag(sync=True)

    # Line

    linestyle_items = traitlets.List().tag(sync=True)
    linestyle_selected = traitlets.Int(allow_none=True).tag(sync=True)

    # Vectors

    vx_att_items = traitlets.List().tag(sync=True)
    vx_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    vy_att_items = traitlets.List().tag(sync=True)
    vy_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    def __init__(self, layer_state):
        super().__init__()

        self.layer_state = layer_state
        self.glue_state = layer_state

        # Color

        link_glue_choices(self, layer_state, "cmap_mode")
        link_glue_choices(self, layer_state, "cmap_att")

        self.cmap_items = [
            {"text": cmap[0], "value": cmap[1].name} for cmap in colormaps.members
        ]

        # Points

        link_glue_choices(self, layer_state, "points_mode")
        link_glue_choices(self, layer_state, "size_mode")
        link_glue_choices(self, layer_state, "size_att")

        link_glue(self, "dpi", layer_state.viewer_state)

        # TODO: make sliders for dpi and size scaling logarithmic

        # FIXME: moving any sliders causes a change in the colormap

        # Line

        link_glue_choices(self, layer_state, "linestyle")

        # Vectors

        link_glue_choices(self, layer_state, "vx_att")
        link_glue_choices(self, layer_state, "vy_att")

    def vue_set_colormap(self, data):
        cmap = None
        for member in colormaps.members:
            if member[1].name == data:
                cmap = member[1]
                break
        self.layer_state.cmap = cmap
