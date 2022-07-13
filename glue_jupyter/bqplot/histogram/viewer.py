from glue.core.subset import roi_to_subset_state
from glue.core.roi import RangeROI

from glue.viewers.histogram.state import HistogramLayerState
from glue.viewers.histogram.state import HistogramViewerState
from glue_jupyter.common.state_widgets.layer_histogram import HistogramLayerStateWidget
from glue_jupyter.common.state_widgets.viewer_histogram import (
    HistogramViewerStateWidget,
)

from glue.core.exceptions import IncompatibleAttribute
from glue.utils import color2hex


from .layer_artist import BqplotHistogramLayerArtist
from ..common.reactviewer import BqplotBaseViewReact
from ...common.hooks import use_echo_state

import react_ipywidgets as react
import react_ipywidgets.bqplot as bq


import numpy as np

__all__ = ['BqplotHistogramView']


def calculate_bins(
    viewer_state: HistogramViewerState, layer_state: HistogramLayerState
):
    use_echo_state(viewer_state, "hist_x_max")
    use_echo_state(viewer_state, "hist_x_min")
    use_echo_state(viewer_state, "hist_n_bin")
    use_echo_state(viewer_state, "cumulative")
    use_echo_state(viewer_state, "normalize")
    disabled, set_disabled = use_echo_state(layer_state, "disabled")
    disabled_reason, set_disabled_reason = use_echo_state(
        layer_state, "disabled_reason"
    )
    # layer_state.reset_cache()

    try:
        bins, hist_unscaled = layer_state.histogram
        set_disabled(False)
    except IncompatibleAttribute:
        bins = None
        set_disabled(True)
        set_disabled_reason("Could not compute histogram")

    if bins is None:
        return  # can happen when the subset is empty

    if bins.size == 0 or hist_unscaled.sum() == 0:
        return

    hist = hist_unscaled.astype(np.float)
    dx = bins[1] - bins[0]

    if viewer_state.cumulative:
        hist = hist.cumsum()
        if viewer_state.normalize:
            hist /= hist.max()
    elif viewer_state.normalize:
        hist /= hist.sum() * dx

    # TODO this won't work for log ...
    centers = (bins[:-1] + bins[1:]) / 2
    assert len(centers) == len(hist)
    x = centers
    y = hist

    # We have to do the following to make sure that we reset the y_max as
    # needed. We can't simply reset based on the maximum for this layer
    # because other layers might have other values, and we also can't do:
    #
    #   viewer_state.y_max = max(viewer_state.y_max, result[0].max())
    #
    # because this would never allow y_max to get smaller.

    layer_state._y_max = hist.max()
    if viewer_state.y_log:
        layer_state._y_max *= 2
    else:
        layer_state._y_max *= 1.2

    if viewer_state.y_log:
        layer_state._y_min = hist[hist > 0].min() / 10
    else:
        layer_state._y_min = 0

    largest_y_max = max(getattr(layer, "_y_max", 0) for layer in viewer_state.layers)
    if largest_y_max != viewer_state.y_max:
        viewer_state.y_max = largest_y_max

    smallest_y_min = min(
        getattr(layer, "_y_min", np.inf) for layer in viewer_state.layers
    )
    if smallest_y_min != viewer_state.y_min:
        viewer_state.y_min = smallest_y_min

    return x, y


@react.component
def Histogram(
    scale_x,
    scale_y,
    viewer_state: HistogramViewerState,
    layer_state: HistogramLayerState,
):
    visible, set_visible = use_echo_state(layer_state, "visible")
    color, set_color = use_echo_state(layer_state, "color")
    alpha, set_color = use_echo_state(layer_state, "alpha")
    scales = dict(x=scale_x, y=scale_y)
    bins = calculate_bins(viewer_state, layer_state)
    if bins is None:
        x = y = [0, 1]  # dummy data, in case we cannot bin
    else:
        x, y = bins

    bars = bq.Bars(scales=scales, x=x, y=y, colors=[color2hex(color)], visible=visible, opacities=[alpha])
    return bars




class BqplotHistogramView(BqplotBaseViewReact):
    allow_duplicate_data = False
    allow_duplicate_subset = False
    large_data_size = 1e5
    is2d = False

    _state_cls = HistogramViewerState
    _options_cls = HistogramViewerStateWidget
    _data_artist_cls = BqplotHistogramLayerArtist
    _subset_artist_cls = BqplotHistogramLayerArtist
    _layer_style_widget_cls = HistogramLayerStateWidget

    tools = ["bqplot:home", "bqplot:panzoom", "bqplot:xrange"]

    components = {HistogramLayerState: Histogram}

    def _roi_to_subset_state(self, roi):
        # TODO: copy paste from glue/viewers/histogram/qt/data_viewer.py
        # TODO Does subset get applied to all data or just visible data?

        bins = self.state.bins

        x = roi.to_polygon()[0]
        lo, hi = min(x), max(x)

        if lo >= bins.min():
            lo = bins[bins <= lo].max()
        if hi <= bins.max():
            hi = bins[bins >= hi].min()

        roi_new = RangeROI(min=lo, max=hi, orientation="x")

        return roi_to_subset_state(roi_new, x_att=self.state.x_att)

    def redraw(self):
        pass # i don't think we need to do anything
