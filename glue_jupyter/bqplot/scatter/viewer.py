from glue.viewers.scatter.state import ScatterViewerState

from ..common.viewer import BqplotBaseView

from .layer_artist import BqplotScatterLayerArtist
from .viewer_options_widget import ScatterViewerStateWidget
from .layer_style_widget import ScatterLayerStateWidget


class BqplotScatterView(BqplotBaseView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    large_data_size = 1e7

    _state_cls = ScatterViewerState
    _options_cls = ScatterViewerStateWidget
    _data_artist_cls = BqplotScatterLayerArtist
    _subset_artist_cls = BqplotScatterLayerArtist
    _layer_style_widget_cls = ScatterLayerStateWidget
