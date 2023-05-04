import numpy as np

from glue.core.units import UnitConverter
from glue.core.subset import roi_to_subset_state
from glue.core.roi import RangeROI
from glue.viewers.profile.state import ProfileViewerState

from ..common.viewer import BqplotBaseView

from .layer_artist import BqplotProfileLayerArtist

from glue_jupyter.common.state_widgets.layer_profile import ProfileLayerStateWidget
from glue_jupyter.common.state_widgets.viewer_profile import ProfileViewerStateWidget

__all__ = ['BqplotProfileView']


class BqplotProfileView(BqplotBaseView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    is2d = False

    _state_cls = ProfileViewerState
    _options_cls = ProfileViewerStateWidget
    _data_artist_cls = BqplotProfileLayerArtist
    _subset_artist_cls = BqplotProfileLayerArtist
    _layer_style_widget_cls = ProfileLayerStateWidget

    tools = ['bqplot:home', 'bqplot:panzoom', 'bqplot:panzoom_x', 'bqplot:panzoom_y',
             'bqplot:xrange']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state.add_callback('x_att', self._update_axes)
        self.state.add_callback('normalize', self._update_axes)
        self.state.add_callback('x_display_unit', self._update_axes)
        self.state.add_callback('y_display_unit', self._update_axes)
        self._update_axes()

    def _update_axes(self, *args):

        if self.state.x_att is not None:
            if self.state.x_display_unit:
                self.state.x_axislabel = str(self.state.x_att) + f' [{self.state.x_display_unit}]'
            else:
                self.state.x_axislabel = str(self.state.x_att)

        if self.state.normalize:
            self.state.y_axislabel = 'Normalized data values'
        else:
            if self.state.y_display_unit:
                self.state.y_axislabel = f'Data values [{self.state.y_display_unit}]'
            else:
                self.state.y_axislabel = 'Data values'

    def _roi_to_subset_state(self, roi):

        x = roi.to_polygon()[0]
        lo, hi = min(x), max(x)

        # Apply inverse unit conversion, converting from display to native units
        converter = UnitConverter()
        lo, hi = converter.to_native(self.state.reference_data,
                                     self.state.x_att, np.array([lo, hi]),
                                     self.state.x_display_unit)

        # Sometimes unit conversions can cause the min/max to be swapped
        if lo > hi:
            lo, hi = hi, lo

        roi_new = RangeROI(min=lo, max=hi, orientation='x')

        return roi_to_subset_state(roi_new, x_att=self.state.x_att)
