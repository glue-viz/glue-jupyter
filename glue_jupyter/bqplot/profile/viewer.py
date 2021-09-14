import numpy as np

from echo import delay_callback

from glue.core.subset import roi_to_subset_state
from glue.core.roi import RangeROI
from glue.viewers.profile.state import ProfileViewerState
from glue.utils import nanmin, nanmax

from ..common.viewer import BqplotBaseView

from .layer_artist import BqplotProfileLayerArtist

from glue_jupyter.common.state_widgets.layer_profile import ProfileLayerStateWidget
from glue_jupyter.common.state_widgets.viewer_profile import ProfileViewerStateWidget

__all__ = ['BqplotProfileView']


class BqplotProfileViewerState(ProfileViewerState):

    def _reset_y_limits(self, *event):
        if self.normalize:
            super()._reset_y_limits()
        else:
            y_min, y_max = np.inf, -np.inf
            for layer in self.layers:
                if layer.profile is not None:
                    x, y = layer.profile
                y_min = min(y_min, nanmin(y))
                y_max = max(y_max, nanmax(y))
            if y_max > y_min:
                with delay_callback(self, 'y_min', 'y_max'):
                    self.y_min = y_min
                    self.y_max = y_max


class BqplotProfileView(BqplotBaseView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    is2d = False

    _state_cls = BqplotProfileViewerState
    _options_cls = ProfileViewerStateWidget
    _data_artist_cls = BqplotProfileLayerArtist
    _subset_artist_cls = BqplotProfileLayerArtist
    _layer_style_widget_cls = ProfileLayerStateWidget

    tools = ['bqplot:home', 'bqplot:panzoom', 'bqplot:panzoom_x', 'bqplot:panzoom_y',
             'bqplot:xrange']

    def _roi_to_subset_state(self, roi):

        x = roi.to_polygon()[0]
        lo, hi = min(x), max(x)

        roi_new = RangeROI(min=lo, max=hi, orientation='x')

        return roi_to_subset_state(roi_new, x_att=self.state.x_att)
