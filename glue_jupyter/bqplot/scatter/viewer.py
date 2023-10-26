from glue.viewers.scatter.state import ScatterViewerState

from ..common.viewer import BqplotBaseView

from .layer_artist import BqplotScatterLayerArtist

from glue_jupyter.common.state_widgets.layer_scatter import ScatterLayerStateWidget
from glue_jupyter.common.state_widgets.viewer_scatter import ScatterViewerStateWidget

from glue_jupyter.registries import viewer_registry

__all__ = ['BqplotScatterView']


@viewer_registry("scatter")
class BqplotScatterView(BqplotBaseView):

    allow_duplicate_data = False
    allow_duplicate_subset = False

    _state_cls = ScatterViewerState
    _options_cls = ScatterViewerStateWidget
    _data_artist_cls = BqplotScatterLayerArtist
    _subset_artist_cls = BqplotScatterLayerArtist
    _layer_style_widget_cls = ScatterLayerStateWidget

    tools = ['bqplot:home', 'bqplot:panzoom', 'bqplot:rectangle', 'bqplot:circle',
             'bqplot:ellipse', 'bqplot:xrange', 'bqplot:yrange', 'bqplot:polygon', 'bqplot:lasso']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state.add_callback('x_att', self._update_axes)
        self.state.add_callback('y_att', self._update_axes)
        self._update_axes()

    def _update_axes(self, *args):

        if self.state.x_att is not None:
            self.state.x_axislabel = str(self.state.x_att)

        if self.state.y_att is not None:
            self.state.y_axislabel = str(self.state.y_att)
