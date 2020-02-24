import ipyvuetify as v
from glue.core import Subset

__all__ = ['LayerOptionsWidget']


import traitlets
import ipywidgets as widgets
from ..vuetify_helpers import load_template, WidgetCache


class LayerOptionsWidget(v.VuetifyTemplate):
    """
    A widget that contains a way to select layers, and will automatically show
    the options for the selected layer.
    """

    template = load_template('layeroptions.vue', __file__)
    layers = traitlets.List().tag(sync=True, **widgets.widget_serialization)
    selected = traitlets.Int(0).tag(sync=True)

    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer

        widgetCache = WidgetCache()

        def layer_to_dict(layer_artist, index):
            if isinstance(layer_artist.state.layer, Subset):
                label = layer_artist.layer.data.label + ':' + layer_artist.state.layer.label
            else:
                label = layer_artist.state.layer.label

            def make_layer_panel():
                widget_cls = viewer._layer_style_widget_cls
                if isinstance(widget_cls, dict):
                    return widget_cls[type(layer_artist)](layer_artist.state)
                else:
                    return widget_cls(layer_artist.state)

            return {
                'index': index,
                'color': layer_artist.state.color,
                'label': label,
                'visible': layer_artist.state.visible,
                'layer_panel': widgetCache.get_or_create(layer_artist, make_layer_panel),
            }

        def _update_layers_from_glue_state(*args):
            self.layers = [layer_to_dict(layer_artist, i) for i, layer_artist in
                           enumerate(self.viewer.layers)]

        self.viewer.state.add_callback('layers', _update_layers_from_glue_state)
        _update_layers_from_glue_state()

    def vue_toggle_visible(self, index):
        state = self.viewer.layers[index].state
        state.visible = not state.visible

    def vue_set_color(self, data):
        index = data['index']
        color = data['color']
        self.viewer.layers[index].state.color = color
