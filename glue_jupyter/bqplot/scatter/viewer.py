from glue.viewers.scatter.state import ScatterViewerState

from ..common.viewer import BqplotBaseView

from .layer_artist import BqplotScatterLayerArtist

from glue_jupyter.common.state_widgets.layer_scatter import ScatterLayerStateWidget
from glue_jupyter.common.state_widgets.viewer_scatter import ScatterViewerStateWidget

__all__ = ['BqplotScatterView']


class BqplotScatterView(BqplotBaseView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    large_data_size = 1e7

    _state_cls = ScatterViewerState
    _options_cls = ScatterViewerStateWidget
    _data_artist_cls = BqplotScatterLayerArtist
    _subset_artist_cls = BqplotScatterLayerArtist
    _layer_style_widget_cls = ScatterLayerStateWidget

    tools = ['bqplot:home', 'bqplot:panzoom', 'bqplot:rectangle', 'bqplot:circle',
             'bqplot:xrange', 'bqplot:yrange']
