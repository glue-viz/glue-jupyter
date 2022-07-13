from glue.viewers.histogram.state import HistogramLayerState

from glue.viewers.common.layer_artist import LayerArtist

__all__ = ['BqplotHistogramLayerArtist']


class BqplotHistogramLayerArtist(LayerArtist):

    _layer_state_cls = HistogramLayerState
    # component = Histogram

    def __init__(self, view, viewer_state, layer_state=None, layer=None):

        super(BqplotHistogramLayerArtist, self).__init__(
            viewer_state, layer_state=layer_state, layer=layer
        )
