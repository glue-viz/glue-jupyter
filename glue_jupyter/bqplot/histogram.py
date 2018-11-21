import numpy as np
import bqplot
import ipywidgets as widgets
import ipywidgets.widgets.trait_types as tt
from IPython.display import display

from glue.core.layer_artist import LayerArtistBase
from glue.core.roi import RectangularROI, RangeROI
from glue.core.exceptions import IncompatibleAttribute
from glue.core.command import ApplySubsetState
from glue.viewers.histogram.state import HistogramViewerState, HistogramLayerState

from ..link import link, dlink, calculation, link_component_id_to_select_widget, on_change

# FIXME: monkey patch ipywidget to accept anything
tt.Color.validate = lambda self, obj, value: value


class BqplotHistogramLayerArtist(LayerArtistBase):
    _layer_state_cls = HistogramLayerState

    def __init__(self, view, viewer_state, layer, layer_state):
        super(BqplotHistogramLayerArtist, self).__init__(layer)
        self.reset_cache()
        self.view = view
        self.state = layer_state or self._layer_state_cls(viewer_state=viewer_state,
                                                          layer=self.layer)
        self._viewer_state = viewer_state
        if self.state not in self._viewer_state.layers:
            self._viewer_state.layers.append(self.state)
        self.bars = bqplot.Bars(
            scales=self.view.scales, x=[0, 1], y=[0, 1])
        self.view.figure.marks = list(self.view.figure.marks) + [self.bars]
        link((self.state, 'color'), (self.bars, 'colors'),
             lambda x: [x], lambda x: x[0])
        #link((self.bars, 'default_opacities'), (self.state, 'alpha'), lambda x: x[0], lambda x: [x])
        #link((self.bars, 'default_size'), (self.state, 'size'))

        self._viewer_state.add_global_callback(self._update_histogram)
        self.state.add_global_callback(self._update_histogram)
        self.bins = None

    def reset_cache(self):
        self._last_viewer_state = {}
        self._last_layer_state = {}

    def _update_xy_att(self, *args):
        self.update()

    def redraw(self):
        pass

    def clear(self):
        pass

    def _calculate_histogram(self):
        self.bins, self.hist_unscaled = self.state.histogram

    def _scale_histogram(self):
        # TODO: comes from glue/viewers/histogram/layer_artist.py
        if self.bins is None:
            return  # can happen when the subset is empty

        if self.bins.size == 0 or self.hist_unscaled.sum() == 0:
            return

        self.hist = self.hist_unscaled.astype(np.float)
        dx = self.bins[1] - self.bins[0]

        if self._viewer_state.cumulative:
            self.hist = self.hist.cumsum()
            if self._viewer_state.normalize:
                self.hist /= self.hist.max()
        elif self._viewer_state.normalize:
            self.hist /= (self.hist.sum() * dx)

        bottom = 0 if not self._viewer_state.y_log else 1e-100

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
            self.state._y_min = self.hist[self.hist > 0].min() / 10
        else:
            self.state._y_min = 0

        largest_y_max = max(getattr(layer, '_y_max', 0)
                            for layer in self._viewer_state.layers)
        if largest_y_max != self._viewer_state.y_max:
            self._viewer_state.y_max = largest_y_max

        smallest_y_min = min(getattr(layer, '_y_min', np.inf)
                             for layer in self._viewer_state.layers)
        if smallest_y_min != self._viewer_state.y_min:
            self._viewer_state.y_min = smallest_y_min

        self.redraw()

    def _update_visual_attributes(self):

        if not self.enabled:
            return
        # TODO: set visual attrs
        self.redraw()

    def _update_histogram(self, force=False, **kwargs):
        # TODO: comes from glue/viewers/histogram/layer_artist.py
        if (self._viewer_state.hist_x_min is None or
                self._viewer_state.hist_x_max is None or
                self._viewer_state.hist_n_bin is None or
                self._viewer_state.x_att is None or
                self.state.layer is None):
            return
        # Figure out which attributes are different from before. Ideally we shouldn't
        # need this but currently this method is called multiple times if an
        # attribute is changed due to x_att changing then hist_x_min, hist_x_max, etc.
        # If we can solve this so that _update_histogram is really only called once
        # then we could consider simplifying this. Until then, we manually keep track
        # of which properties have changed.

        changed = set()

        if not force:

            for key, value in self._viewer_state.as_dict().items():
                if value != self._last_viewer_state.get(key, None):
                    changed.add(key)

            for key, value in self.state.as_dict().items():
                if value != self._last_layer_state.get(key, None):
                    changed.add(key)

        self._last_viewer_state.update(self._viewer_state.as_dict())
        self._last_layer_state.update(self.state.as_dict())

        if force or any(prop in changed for prop in ('layer', 'x_att', 'hist_x_min', 'hist_x_max', 'hist_n_bin', 'x_log')):
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

    def create_widgets(self):
        self.widget_visible = widgets.Checkbox(description='visible', value=self.state.visible)
        link((self.state, 'visible'), (self.widget_visible, 'value'))
        link((self.state, 'visible'), (self.bars, 'visible'))

        self.widget_color = widgets.ColorPicker(description='color')
        link((self.state, 'color'), (self.widget_color, 'value'))

        return widgets.VBox([self.widget_visible, self.widget_color])
