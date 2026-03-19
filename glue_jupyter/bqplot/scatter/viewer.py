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
        self.state.add_callback('x_log', self._update_x_log)
        self.state.add_callback('y_log', self._update_y_log)
        self.state.add_callback('x_min', self._validate_log_limits)
        self.state.add_callback('y_min', self._validate_log_limits)
        self._update_axes()

    def _update_axes(self, *args):

        if self.state.x_att is not None:
            self.state.x_axislabel = str(self.state.x_att)

        if self.state.y_att is not None:
            self.state.y_axislabel = str(self.state.y_att)

    def _update_x_log(self, *args):
        self._replace_scale('x')

    def _update_y_log(self, *args):
        self._replace_scale('y')

    def _validate_log_limits(self, *args):
        # When the browser syncs state via GlueState, it sends the full
        # state dict including stale x_min/x_max alongside the new x_log
        # value. Since x_log has higher update priority, it is applied
        # first, but then the stale (possibly negative) limits overwrite
        # the values computed by _reset_x/y_limits. We detect and fix
        # this by forcing a limit recalculation when log is active but
        # the limits are non-positive.
        if self.state.x_log and self.state.x_min is not None and self.state.x_min <= 0:
            self.state._reset_x_limits()
        if self.state.y_log and self.state.y_min is not None and self.state.y_min <= 0:
            self.state._reset_y_limits()
