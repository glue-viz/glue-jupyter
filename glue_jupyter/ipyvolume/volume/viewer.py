from glue_jupyter.common.state3d import VolumeViewerState

from .layer_artist import IpyvolumeVolumeLayerArtist
from .layer_style_widget import Volume3DLayerStateWidget

from ..scatter.layer_artist import IpyvolumeScatterLayerArtist
from ..scatter.layer_style_widget import Scatter3DLayerStateWidget

from ..common.viewer_options_widget import Viewer3DStateWidget
from ..common.viewer import IpyvolumeBaseView

__all__ = ['IpyvolumeVolumeView']


class IpyvolumeVolumeView(IpyvolumeBaseView):

    large_data_size = 1e8

    _state_cls = VolumeViewerState
    _options_cls = Viewer3DStateWidget
    _data_artist_cls = IpyvolumeVolumeLayerArtist
    _subset_artist_cls = IpyvolumeVolumeLayerArtist
    _layer_style_widget_cls = {IpyvolumeVolumeLayerArtist: Volume3DLayerStateWidget,
                               IpyvolumeScatterLayerArtist: Scatter3DLayerStateWidget}

    def get_data_layer_artist(self, layer=None, layer_state=None):
        if layer.ndim == 1:
            cls = IpyvolumeScatterLayerArtist
        else:
            cls = IpyvolumeVolumeLayerArtist
        return self.get_layer_artist(cls, layer=layer, layer_state=layer_state)

    def get_subset_layer_artist(self, layer=None, layer_state=None):
        return self.get_data_layer_artist(layer, layer_state)
