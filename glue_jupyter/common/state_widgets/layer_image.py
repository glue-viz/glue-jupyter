from ipywidgets import Checkbox, FloatSlider, ColorPicker, VBox, Dropdown
from glue.config import colormaps
from glue.utils import color2hex

from ...link import link

import ipyvuetify as v
import traitlets
from ...state_traitlets_helpers import GlueState
from ...vuetify_helpers import load_template, link_glue_choices, link_glue

__all__ = ['ImageLayerStateWidget', 'ImageSubsetLayerStateWidget']


class ImageLayerStateWidget(v.VuetifyTemplate):
    template = load_template('layer_image.vue', __file__)

    glue_state = GlueState().tag(sync=True)

    attribute_items = traitlets.List().tag(sync=True)
    attribute_selected = traitlets.Int(allow_none=True).tag(sync=True)

    stretch_items = traitlets.List().tag(sync=True)
    stretch_selected = traitlets.Int(allow_none=True).tag(sync=True)

    percentile_items = traitlets.List().tag(sync=True)
    percentile_selected = traitlets.Int(allow_none=True).tag(sync=True)

    colormap_items = traitlets.List().tag(sync=True)
    color_mode = traitlets.Unicode().tag(sync=True)

    def __init__(self, layer_state):
        super().__init__()

        self.layer_state = layer_state
        self.glue_state = layer_state

        link_glue_choices(self, layer_state, 'attribute')
        link_glue_choices(self, layer_state, 'stretch')
        link_glue_choices(self, layer_state, 'percentile')

        self.colormap_items = [dict(
            text=cmap[0],
            value=cmap[1].name
        ) for cmap in colormaps.members]

        link_glue(self, 'color_mode', layer_state.viewer_state)

    def vue_set_colormap(self, data):
        print(f'{data}')

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
