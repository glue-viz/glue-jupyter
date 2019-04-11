
from glue.viewers.common.viewer import Viewer
from glue.core.layer_artist import LayerArtistContainer
from glue.core import message as msg
from glue.core.subset import Subset

from glue_jupyter.utils import _update_not_none

from .link import link


class IPyWidgetLayerArtistContainer(LayerArtistContainer):

    def __init__(self):
        super(IPyWidgetLayerArtistContainer, self).__init__()
        pass  #print('layer artist created')


class IPyWidgetView(Viewer):

    _layer_artist_container_cls = IPyWidgetLayerArtistContainer

    def add_data(self, data, color=None, alpha=None, **layer_state):

        result = super().add_data(data)

        if not result:
            return

        layer = list(self._layer_artist_container[data])[-1]

        layer_state = dict(layer_state)
        _update_not_none(layer_state, color=color, alpha=alpha)
        layer.state.update_from_dict(layer_state)

        return True

    def _update_subset(self, message):
        # TODO: move improvement here to glue-core
        if message.subset in self._layer_artist_container:
            for layer_artist in self._layer_artist_container[message.subset]:
                if isinstance(message, msg.SubsetUpdateMessage) and message.attribute not in ['subset_state']:
                    pass
                else:
                    layer_artist.update()
            self.redraw()

    def get_layer_artist(self, cls, layer=None, layer_state=None):
        return cls(self, self.state, layer=layer, layer_state=layer_state)

    def _add_layer_tab(self, layer):
        if isinstance(self._layer_style_widget_cls, dict):
            layer_tab = self._layer_style_widget_cls[type(layer)](layer.state)
        else:
            layer_tab = self._layer_style_widget_cls(layer.state)
        self.tab.children = self.tab.children + (layer_tab, )
        if isinstance(layer.layer, Subset):
            label = '{data_label}:{subset_label}'.format(data_label=layer.layer.data.label, subset_label=layer.layer.label)
        else:
            label = layer.layer.label
        self.tab.set_title(len(self.tab.children)-1, label)
