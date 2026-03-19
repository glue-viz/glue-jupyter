from ipywidgets import (Checkbox, VBox, ColorPicker, Dropdown, FloatSlider,
                        FloatLogSlider)

from glue.core.subset import Subset
from glue.utils import color2hex

from glue_jupyter.widgets import Color
from glue_jupyter.widgets.glue_float_field import GlueFloatField
from glue_jupyter.widgets.linked_dropdown import LinkedDropdown

from ...link import link

__all__ = ['Volume3DLayerStateWidget']


class Volume3DLayerStateWidget(VBox):

    def __init__(self, layer_state):

        self.state = layer_state

        self.widget_lighting = Checkbox(description='lighting', value=self.state.lighting)
        link((self.state, 'lighting'), (self.widget_lighting, 'value'))

        render_methods = 'NORMAL MAX_INTENSITY'.split()
        self.widget_render_method = Dropdown(options=render_methods,
                                             value=self.state.render_method,
                                             description='method')
        link((self.state, 'render_method'), (self.widget_render_method, 'value'))

        if self.state.vmin is None:
            self.state.vmin = 0

        self.widget_data_min = GlueFloatField(label="vmin", initial_value=self.state.vmin)
        link((self.state, 'vmin'), (self.widget_data_min, 'value'))

        if self.state.vmax is None:
            self.state.vmax = 1

        self.widget_data_max = GlueFloatField(label="vmax", initial_value=self.state.vmax)
        link((self.state, 'vmax'), (self.widget_data_max, 'value'))

        self.widget_clamp_min = Checkbox(description='clamp minimum', value=self.state.clamp_min)
        link((self.state, 'clamp_min'), (self.widget_clamp_min, 'value'))

        self.widget_clamp_max = Checkbox(description='clamp maximum', value=self.state.clamp_max)
        link((self.state, 'clamp_max'), (self.widget_clamp_max, 'value'))

        if isinstance(layer_state.layer, Subset):
            self.widget_color = ColorPicker(value=color2hex(self.state.color), description='color')
            link((self.state, 'color'), (self.widget_color, 'value'), color2hex)
        else:
            self.widget_color = Color(state=self.state, cmap_mode_attr='color_mode', cmap_att=None)

        if self.state.alpha is None:
            self.state.alpha = 1

        self.widget_opacity = FloatSlider(description='opacity', min=0, max=1,
                                          value=self.state.alpha, step=0.001)
        link((self.state, 'alpha'), (self.widget_opacity, 'value'))

        self.widget_opacity_scale = FloatLogSlider(description='opacity scale', base=10,
                                                   min=-3, max=3, step=0.01,
                                                   value=self.state.opacity_scale)
        link((self.state, 'opacity_scale'), (self.widget_opacity_scale, 'value'))

        self.widget_stretch = LinkedDropdown(self.state, 'stretch',
                                             ui_name='stretch',
                                             label='stretch')

        # FIXME: this should be fixed
        # self.widget_reset_zoom = Button(description="Reset zoom")
        # self.widget_reset_zoom.on_click(self.state.viewer_state.reset_limits)

        super().__init__([self.widget_render_method, self.widget_lighting,
                          self.widget_data_min, self.widget_data_max,
                          self.widget_clamp_min, self.widget_clamp_max,
                          self.widget_color, self.widget_opacity,
                          self.widget_opacity_scale, self.widget_stretch])
