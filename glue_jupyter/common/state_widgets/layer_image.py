from ipywidgets import Checkbox, FloatSlider, ColorPicker, VBox
from glue.config import colormaps
from glue.utils import color2hex

from ...link import link

import ipyvuetify as v
import traitlets
from ...state_traitlets_helpers import GlueState
from ...vuetify_helpers import link_glue_choices, link_glue

__all__ = ['ImageLayerStateWidget', 'ImageSubsetLayerStateWidget']


class ImageLayerStateWidget(v.VuetifyTemplate):
    template_file = (__file__, 'layer_image.vue')

    glue_state = GlueState().tag(sync=True)

    # TODO: expose toggle to turn on image and/or contour

    attribute_items = traitlets.List().tag(sync=True)
    attribute_selected = traitlets.Int(allow_none=True).tag(sync=True)

    stretch_items = traitlets.List().tag(sync=True)
    stretch_selected = traitlets.Int(allow_none=True).tag(sync=True)

    percentile_items = traitlets.List().tag(sync=True)
    percentile_selected = traitlets.Int(allow_none=True).tag(sync=True)

    colormap_items = traitlets.List().tag(sync=True)
    color_mode = traitlets.Unicode().tag(sync=True)

    c_levels_txt = traitlets.Unicode().tag(sync=True)
    c_levels_txt_editing = False
    c_levels_error = traitlets.Unicode().tag(sync=True)

    has_contour = traitlets.Bool().tag(sync=True)

    def __init__(self, layer_state):
        super().__init__()

        self.layer_state = layer_state
        self.glue_state = layer_state

        self.has_contour = hasattr(layer_state, "contour_visible")

        link_glue_choices(self, layer_state, 'attribute')
        link_glue_choices(self, layer_state, 'stretch')
        link_glue_choices(self, layer_state, 'percentile')

        self.colormap_items = [dict(
            text=cmap[0],
            value=cmap[1].name
        ) for cmap in colormaps.members]

        link_glue(self, 'color_mode', layer_state.viewer_state)

        # we only go from glue state to the text version of the level list
        # the other way around is handled in _on_change_c_levels_txt
        if self.has_contour:
            def levels_to_text(*_ignore):
                if not self.c_levels_txt_editing:
                    text = ", ".join('%g' % v for v in self.glue_state.levels)
                    self.c_levels_txt = text

            self.glue_state.add_callback('levels', levels_to_text)

    @traitlets.observe('c_levels_txt')
    def _on_change_c_levels_txt(self, change):
        try:
            self.c_levels_txt_editing = True
            try:
                parts = change['new'].split(',')
                float_list_str = [float(v.strip()) for v in parts]
            except Exception as e:
                self.c_levels_error = str(e)
                return

            if self.glue_state.level_mode == "Custom":
                self.glue_state.levels = float_list_str
            self.c_levels_error = ''
        finally:
            self.c_levels_txt_editing = False

    def vue_set_colormap(self, data):
        cmap = None
        for member in colormaps.members:
            if member[1].name == data:
                cmap = member[1]
                break

        self.layer_state.cmap = cmap


class ImageSubsetLayerStateWidget(VBox):

    def __init__(self, layer_state):

        self.state = layer_state

        self.widget_visible = Checkbox(description='visible', value=self.state.visible)
        link((self.state, 'visible'), (self.widget_visible, 'value'))

        self.widget_opacity = FloatSlider(min=0, max=1, step=0.01, value=self.state.alpha,
                                          description='opacity')
        link((self.state, 'alpha'), (self.widget_opacity, 'value'))

        self.widget_color = ColorPicker(description='color')
        link((self.state, 'color'), (self.widget_color, 'value'), color2hex)

        super().__init__([self.widget_visible, self.widget_opacity, self.widget_color])
