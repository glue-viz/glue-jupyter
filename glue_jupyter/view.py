from glue.viewers.common.viewer import Viewer
from glue.core.layer_artist import LayerArtistContainer
from glue.core import message as msg
from glue.core.subset import Subset

from glue_jupyter.utils import _update_not_none

class IPyWidgetLayerArtistContainer(LayerArtistContainer):

    def __init__(self):
        super(IPyWidgetLayerArtistContainer, self).__init__()
        pass  #print('layer artist created')


class IPyWidgetView(Viewer):

    _layer_artist_container_cls = IPyWidgetLayerArtistContainer

    def __init__(self, session, state=None):
        super(IPyWidgetView, self).__init__(session, state=state)

    # TODO: a lot of this comes from DataViewerWithState
    def register_to_hub(self, hub):
        super(IPyWidgetView, self).register_to_hub(hub)

        hub.subscribe(self, msg.SubsetCreateMessage,
                      handler=self._add_subset,
                      filter=self._subset_has_data)

        hub.subscribe(self, msg.SubsetUpdateMessage,
                      handler=self._update_subset,
                      filter=self._has_data_or_subset)

        hub.subscribe(self, msg.SubsetDeleteMessage,
                      handler=self._remove_subset,
                      filter=self._has_data_or_subset)

        hub.subscribe(self, msg.NumericalDataChangedMessage,
                      handler=self._update_data,
                      filter=self._has_data_or_subset)

        # hub.subscribe(self, msg.DataCollectionDeleteMessage,
        #               handler=self._remove_data)

        hub.subscribe(self, msg.ComponentsChangedMessage,
                      handler=self._update_data,
                      filter=self._has_data_or_subset)

        # hub.subscribe(self, msg.SettingsChangeMessage,
        #               self._update_appearance_from_settings,
        #               filter=self._is_appearance_settings)


    def add_data(self, data, color=None, alpha=None, **layer_state):

        # Check if data already exists in viewer
        if not self.allow_duplicate_data and data in self._layer_artist_container:
            return None

        if self.large_data_size is not None and data.size >= self.large_data_size:
            proceed = self.warn('Add large data set?', 'Data set {0:s} has {1:d} points, and '
                                'may render slowly.'.format(data.label, data.size),
                                default='Cancel', setting='show_large_data_warning')
            if not proceed:
                return None

        if data not in self.session.data_collection:
            raise IncompatibleDataException("Data not in DataCollection")

        # Create layer artist and add to container
        layer = self.get_data_layer_artist(data)

        if layer is None:
            return None

        self._layer_artist_container.append(layer)
        layer_state = dict(layer_state)
        _update_not_none(layer_state, color=color, alpha=alpha)
        layer.update()
        layer.state.update_from_dict(layer_state)

        # Add existing subsets to viewer
        for subset in data.subsets:
            self.add_subset(subset)

        return layer

    def remove_subset(self, subset):
        if subset in self._layer_artist_container:
            self._layer_artist_container.pop(subset)
            self.redraw()

    def _remove_subset(self, message):
        self.remove_subset(message.subset)

    def _add_subset(self, message):
        self.add_subset(message.subset)

    def _update_subset(self, message):
        if message.subset in self._layer_artist_container:
            for layer_artist in self._layer_artist_container[message.subset]:
                if isinstance(message, msg.SubsetUpdateMessage) and message.attribute not in ['subset_state']:
                    pass
                else:
                    layer_artist.update()
            self.redraw()

    def _subset_has_data(self, x):
        return x.sender.data in self._layer_artist_container.layers

    def _has_data_or_subset(self, x):
        return x.sender in self._layer_artist_container.layers

    def get_layer_artist(self, cls, layer=None, layer_state=None):
        return cls(self, self.state, layer=layer, layer_state=layer_state)

    def _update_data(self, message):
        if message.data in self._layer_artist_container:
            for layer_artist in self._layer_artist_container:
                if isinstance(layer_artist.layer, Subset):
                    if layer_artist.layer.data is message.data:
                        layer_artist.update()
                else:
                    if layer_artist.layer is message.data:
                        layer_artist.update()
            self.redraw()

    def _add_layer_tab(self, layer):
        layer_tab = layer.create_widgets()
        self.tab.children = self.tab.children + (layer_tab, )
        if isinstance(layer.layer, Subset):
            label = '{data_label}:{subset_label}'.format(data_label=layer.layer.data.label, subset_label=layer.layer.label)
        else:
            label = layer.layer.label
        self.tab.set_title(len(self.tab.children)-1, label)
