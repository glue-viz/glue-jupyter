from ipywidgets import (Checkbox, VBox, ColorPicker, Dropdown, FloatSlider,
                        FloatLogSlider)

from glue.utils import color2hex

from ...link import link, dlink

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

        self.size_options = [32, 64, 128, 128+64, 256, 256+128, 512]
        options = [(str(k), k) for k in self.size_options]
        self.widget_max_resolution = Dropdown(options=options, value=128,
                                              description='max resolution')
        link((self.state, 'max_resolution'), (self.widget_max_resolution, 'value'))

        if self.state.vmin is None:
            self.state.vmin = 0

        self.widget_data_min = FloatSlider(description='min', min=0, max=1,
                                           value=self.state.vmin, step=0.001)
        link((self.state, 'vmin'), (self.widget_data_min, 'value'))
        dlink((self.state, 'data_min'), (self.widget_data_min, 'min'))
        dlink((self.state, 'data_max'), (self.widget_data_min, 'max'))

        if self.state.vmax is None:
            self.state.vmax = 1

        self.widget_data_max = FloatSlider(description='max', min=0, max=1,
                                           value=self.state.vmax, step=0.001)
        link((self.state, 'vmax'), (self.widget_data_max, 'value'))
        dlink((self.state, 'data_min'), (self.widget_data_max, 'min'))
        dlink((self.state, 'data_max'), (self.widget_data_max, 'max'))

        self.widget_clamp_min = Checkbox(description='clamp minimum', value=self.state.clamp_min)
        link((self.state, 'clamp_min'), (self.widget_clamp_min, 'value'))

        self.widget_clamp_max = Checkbox(description='clamp maximum', value=self.state.clamp_max)
        link((self.state, 'clamp_max'), (self.widget_clamp_max, 'value'))

        self.widget_color = ColorPicker(value=color2hex(self.state.color), description='color')
        link((self.state, 'color'), (self.widget_color, 'value'), color2hex)

        if self.state.alpha is None:
            self.state.alpha = 1

        self.widget_opacity = FloatSlider(description='opacity', min=0, max=1,
                                          value=self.state.alpha, step=0.001)
        link((self.state, 'alpha'), (self.widget_opacity, 'value'))

        self.widget_opacity_scale = FloatLogSlider(description='opacity scale', base=10,
                                                   min=-3, max=3, step=0.01,
                                                   value=self.state.opacity_scale)
        link((self.state, 'opacity_scale'), (self.widget_opacity_scale, 'value'))

        # FIXME: this should be fixed
        # self.widget_reset_zoom = Button(description="Reset zoom")
        # self.widget_reset_zoom.on_click(self.state.viewer_state.reset_limits)

        super().__init__([self.widget_render_method, self.widget_lighting,
                          self.widget_data_min, self.widget_data_max,
                          self.widget_clamp_min, self.widget_clamp_max,
                          self.widget_max_resolution,  # self.widget_reset_zoom,
                          self.widget_color, self.widget_opacity,
                          self.widget_opacity_scale])
