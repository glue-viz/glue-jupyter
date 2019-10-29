from glue.core import Subset
from ipywidgets import VBox, Dropdown

__all__ = ['LayerOptionsWidget']


class LayerOptionsWidget(VBox):
    """
    A widget that contains a way to select layers, and will automatically show
    the options for the selected layer.
    """

    def __init__(self, viewer):

        self.viewer = viewer
        self._layer_dropdown = Dropdown(description="Layer")

        self.viewer.state.add_callback('layers', self._update_ui_from_glue_state)
        self._update_ui_from_glue_state()

        self._layer_dropdown.observe(self._update_layer_options_panel, 'value')

        super(LayerOptionsWidget, self).__init__([self._layer_dropdown])

    def _update_ui_from_glue_state(self, *args):

        layers = self.viewer.layers

        labels = []

        for layer_artist in layers:

            if isinstance(layer_artist.state.layer, Subset):
                label = layer_artist.state.layer.data.label + ':' + layer_artist.state.layer.label
            else:
                label = layer_artist.state.layer.label

            labels.append(label)

        current = self._layer_dropdown.value

        self._layer_dropdown.options = list(zip(labels, layers))

        if len(layers) > 0:
            if current in layers:
                self._layer_dropdown.value = current
            else:
                self._layer_dropdown.value = layers[0]

    def _update_layer_options_panel(self, *args):

        layer_artist = self._layer_dropdown.value

        if layer_artist is None:
            return

        widget_cls = self.viewer._layer_style_widget_cls
        if isinstance(widget_cls, dict):
            layer_panel = widget_cls[type(layer_artist)](layer_artist.state)
        else:
            layer_panel = widget_cls(layer_artist.state)

        self.children = self.children[:1] + (layer_panel,)
