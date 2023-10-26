from glue_jupyter.common.state3d import Scatter3DViewerState
from .layer_artist import IpyvolumeScatterLayerArtist
from .layer_style_widget import Scatter3DLayerStateWidget
from ..common.viewer_options_widget import Viewer3DStateWidget
from ..common.viewer import IpyvolumeBaseView

__all__ = ['IpyvolumeScatterView']


class IpyvolumeScatterView(IpyvolumeBaseView):

    allow_duplicate_data = False
    allow_duplicate_subset = False

    _state_cls = Scatter3DViewerState
    _options_cls = Viewer3DStateWidget
    _data_artist_cls = IpyvolumeScatterLayerArtist
    _subset_artist_cls = IpyvolumeScatterLayerArtist
    _layer_style_widget_cls = Scatter3DLayerStateWidget

    def get_data_layer_artist(self, layer=None, layer_state=None):
        return self.get_layer_artist(self._data_artist_cls, layer=layer, layer_state=layer_state)

    def get_subset_layer_artist(self, layer=None, layer_state=None):
        return self.get_layer_artist(self._subset_artist_cls, layer=layer, layer_state=layer_state)
