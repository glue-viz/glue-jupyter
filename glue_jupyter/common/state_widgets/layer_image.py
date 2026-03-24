from ipywidgets import Checkbox, FloatSlider, ColorPicker, VBox
from glue.utils import color2hex

from ...link import link

import ipyvuetify as v
import traitlets

from echo.vue import autoconnect_callbacks_to_vue

from ...vuetify_helpers import cmap_extras

__all__ = ['ImageLayerStateWidget', 'ImageSubsetLayerStateWidget']


class ImageLayerStateWidget(v.VuetifyTemplate):
    template_file = (__file__, 'layer_image.vue')

    c_levels_txt = traitlets.Unicode().tag(sync=True)
    c_levels_txt_editing = False
    c_levels_error = traitlets.Unicode().tag(sync=True)

    has_contour = traitlets.Bool().tag(sync=True)

    def __init__(self, layer_state):
        super().__init__()

        self.layer_state = layer_state

        self.has_contour = hasattr(layer_state, "contour_visible")

        extras = {'cmap': cmap_extras(self)}
        if self.has_contour:
            extras.update({'contour_visible': 'bool',
                           'bitmap_visible': 'bool',
                           'level_mode': 'text'})

        autoconnect_callbacks_to_vue(layer_state, self, extras=extras)

        autoconnect_callbacks_to_vue(layer_state.viewer_state, self,
                                     only={'color_mode': 'text'})

        if self.has_contour:
            # Sync contour levels to editable text
            def levels_to_text(*_ignore):
                if not self.c_levels_txt_editing:
                    text = ", ".join('%g' % v for v in layer_state.levels)
                    self.c_levels_txt = text

            layer_state.add_callback('levels', levels_to_text)

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

            if self.layer_state.level_mode == "Custom":
                self.layer_state.levels = float_list_str
            self.c_levels_error = ''
        finally:
            self.c_levels_txt_editing = False


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
