import ipyvuetify as v
from glue.core import Subset

from glue.utils import avoid_circular

__all__ = ['LayerOptionsWidget']


class LayerOptionsWidget(v.Container):
    """
    A widget that contains a way to select layers, and will automatically show
    the options for the selected layer.
    """

    def __init__(self, viewer):

        self._layers_last = []

        self.viewer = viewer
        self._layer_dropdown = v.Select(label="Layer", v_model=None)

        self.viewer.state.add_callback('layers', self._update_ui_from_glue_state)
        self._update_ui_from_glue_state()

        self._layer_dropdown.on_event('change', self._update_layer_options_panel)

        super(LayerOptionsWidget, self).__init__(children=[self._layer_dropdown])

    def _update_ui_from_glue_state(self, *args):

        # If layer property changes, layers will have a callback event, but we
        # should ignore it since here we are only interested in actual changes
        # to the content of the layers list.
        if (len(self.viewer.layers) == len(self._layers_last) and
            all([layer1 is layer2 for (layer1, layer2) in
                 zip(self._layers_last, self.viewer.layers)])):
            return

        layers = self.viewer.layers

        labels = []

        for layer_artist in layers:

            if isinstance(layer_artist.state.layer, Subset):
                label = layer_artist.state.layer.data.label + ':' + layer_artist.state.layer.label
            else:
                label = layer_artist.state.layer.label

            labels.append(label)

        current = self._layer_dropdown.v_model

        self._layer_dropdown.items = [{'text': label, 'value': layers.index(layer)}
                                       for (label, layer) in zip(labels, layers)]

        if len(layers) > 0:
            if current is not None and current < len(layers):
                self._layer_dropdown.v_model = current
            else:
                self._layer_dropdown.v_model = 0

        self._layers_last = layers

        self._update_layer_options_panel()

    @avoid_circular
    def _update_layer_options_panel(self, *args):

        layer_artist = self._layer_dropdown.v_model

        if layer_artist is None:
            return

        layer_artist = self.viewer.layers[layer_artist]

        widget_cls = self.viewer._layer_style_widget_cls
        if isinstance(widget_cls, dict):
            layer_panel = widget_cls[type(layer_artist)](layer_artist.state)
        else:
            layer_panel = widget_cls(layer_artist.state)

        if len(self.children) == 2 and hasattr(self.children[1], 'cleanup'):
            self.children[1].cleanup()

        self.children = self.children[:1] + [layer_panel]
