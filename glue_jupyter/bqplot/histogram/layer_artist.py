import numpy as np
import bqplot

from glue.core.exceptions import IncompatibleAttribute
from glue.viewers.histogram.state import HistogramLayerState
from glue.viewers.common.layer_artist import LayerArtist
from glue.utils import color2hex

from ...link import link, dlink

__all__ = ['BqplotHistogramLayerArtist']


class BqplotHistogramLayerArtist(LayerArtist):

    _layer_state_cls = HistogramLayerState

    def __init__(self, view, viewer_state, layer_state=None, layer=None):

        super(BqplotHistogramLayerArtist, self).__init__(viewer_state,
                                                         layer_state=layer_state, layer=layer)

        self.view = view

        self.bars = bqplot.Bars(
            scales=self.view.scales, x=[0, 1], y=[0, 1])

        self.view.figure.marks = list(self.view.figure.marks) + [self.bars]

        dlink((self.state, 'color'), (self.bars, 'colors'), lambda x: [color2hex(x)])
        dlink((self.state, 'alpha'), (self.bars, 'opacities'), lambda x: [x])

        self._viewer_state.add_global_callback(self._update_histogram)
        self.state.add_global_callback(self._update_histogram)
        self.bins = None

        link((self.state, 'visible'), (self.bars, 'visible'))

    def remove(self):
        marks = self.view.figure.marks[:]
        marks.remove(self.bars)
        self.bars = None
        self.view.figure.marks = marks
        return super().remove()

    def _update_xy_att(self, *args):
        self.update()

    def _calculate_histogram(self):
        try:
            self.bins, self.hist_unscaled = self.state.histogram
        except IncompatibleAttribute:
            self.disable('Could not compute histogram')
            self.bins = self.hist_unscaled = None

    def _scale_histogram(self):
        # TODO: comes from glue/viewers/histogram/layer_artist.py
        if self.bins is None:
            return  # can happen when the subset is empty

        if self.bins.size == 0:
            return

        self.hist = self.hist_unscaled.astype(float)
        dx = self.bins[1] - self.bins[0]

        if self._viewer_state.cumulative:
            self.hist = self.hist.cumsum()
            if self._viewer_state.normalize and self.hist.max() > 0:
                self.hist /= self.hist.max()
        elif self._viewer_state.normalize and self.hist.sum() > 0:
            self.hist /= (self.hist.sum() * dx)

        # TODO this won't work for log ...
        centers = (self.bins[:-1] + self.bins[1:]) / 2
        assert len(centers) == len(self.hist)
        self.bars.x = centers
        self.bars.y = self.hist

        # We have to do the following to make sure that we reset the y_max as
        # needed. We can't simply reset based on the maximum for this layer
        # because other layers might have other values, and we also can't do:
        #
        #   self._viewer_state.y_max = max(self._viewer_state.y_max, result[0].max())
        #
        # because this would never allow y_max to get smaller.

        self.state._y_max = self.hist.max()
        if self._viewer_state.y_log:
            self.state._y_max *= 2
        else:
            self.state._y_max *= 1.2

        if self._viewer_state.y_log:
            keep = self.hist > 0
            if np.any(keep):
                self.state._y_min = self.hist[keep].min() / 10
            else:
                self.state._y_min = 0
        else:
            self.state._y_min = 0

        largest_y_max = max(getattr(layer, '_y_max', 0)
                            for layer in self._viewer_state.layers)
        if np.isfinite(largest_y_max) and largest_y_max != self._viewer_state.y_max:
            self._viewer_state.y_max = largest_y_max

        smallest_y_min = min(getattr(layer, '_y_min', np.inf)
                             for layer in self._viewer_state.layers)
        if np.isfinite(smallest_y_min) and smallest_y_min != self._viewer_state.y_min:
            self._viewer_state.y_min = smallest_y_min

        self.redraw()

    def _update_visual_attributes(self):

        if not self.enabled:
            return
        # TODO: set other visual attrs
        sorted_layers = sorted(self.view.layers, key=lambda layer: layer.state.zorder)
        self.view.figure.marks = [layer.bars for layer in sorted_layers]
        self.redraw()

    def _update_histogram(self, force=False, **kwargs):

        # TODO: comes from glue/viewers/histogram/layer_artist.py

        if (self.bars is None or
                self._viewer_state.hist_x_min is None or
                self._viewer_state.hist_x_max is None or
                self._viewer_state.hist_n_bin is None or
                self._viewer_state.x_att is None or
                self.state.layer is None):
            return

        # NOTE: we need to evaluate this even if force=True so that the cache
        # of updated properties is up to date after this method has been called.
        changed = self.pop_changed_properties()

        if force or any(prop in changed for prop in ('layer', 'x_att', 'hist_x_min',
                                                     'hist_x_max', 'hist_n_bin', 'x_log')):
            self._calculate_histogram()
            force = True  # make sure scaling and visual attributes are updated

        if force or any(prop in changed for prop in ('y_log', 'normalize', 'cumulative')):
            self._scale_histogram()

        if force or any(prop in changed for prop in ('alpha', 'color', 'zorder', 'visible')):
            self._update_visual_attributes()

    def update(self):
        self.state.reset_cache()
        self._update_histogram(force=True)
        self.redraw()
