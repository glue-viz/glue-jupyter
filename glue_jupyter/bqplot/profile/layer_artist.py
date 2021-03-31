from __future__ import absolute_import, division, print_function

import sys
import warnings

import numpy as np

from glue.core import BaseData
from glue.utils import defer_draw, nanmin, nanmax, color2hex
from glue.viewers.profile.state import ProfileLayerState
from glue.core.exceptions import IncompatibleAttribute, IncompatibleDataException

import bqplot

from glue.viewers.common.layer_artist import LayerArtist

from ...link import dlink

__all__ = ['BqplotProfileLayerArtist']


class BqplotProfileLayerArtist(LayerArtist):

    _layer_state_cls = ProfileLayerState

    def __init__(self, view, viewer_state, layer_state=None, layer=None):

        super().__init__(viewer_state, layer_state=layer_state, layer=layer)

        # Watch for changes in the viewer state which would require the
        # layers to be redrawn
        self._viewer_state.add_global_callback(self._update_profile)
        self.state.add_global_callback(self._update_profile)

        self.view = view

        self.line_mark = bqplot.Lines(scales=self.view.scales, x=[0, 1], y=[0, 1])

        self.view.figure.marks = list(self.view.figure.marks) + [self.line_mark]

        dlink((self.state, 'color'), (self.line_mark, 'colors'), lambda x: [color2hex(x)])
        dlink((self.state, 'alpha'), (self.line_mark, 'opacities'), lambda x: [x])

        self.line_mark.colors = [color2hex(self.state.color)]
        self.line_mark.opacities = [self.state.alpha]

    def remove(self):
        marks = self.view.figure.marks[:]
        marks.remove(self.line_mark)
        self.line_mark = None
        self.view.figure.marks = marks
        return super().remove()

    def _calculate_profile(self, reset=False):
        try:
            self._calculate_profile_thread(reset=reset)
        except Exception:
            self._calculate_profile_error(sys.exc_info())
        else:
            self._calculate_profile_postthread()

    def _calculate_profile_thread(self, reset=False):
        # We need to ignore any warnings that happen inside the thread
        # otherwise the thread tries to send these to the glue logger (which
        # uses Qt), which then results in this kind of error:
        # QObject::connect: Cannot queue arguments of type 'QTextCursor'
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if reset:
                self.state.reset_cache()
            self.state.update_profile(update_limits=False)

    def _calculate_profile_postthread(self):

        # It's possible for this method to get called but for the state to have
        # been updated in the mean time to have a histogram that raises an
        # exception (for example an IncompatibleAttribute). If any errors happen
        # here, we simply ignore them since _calculate_histogram_error will get
        # called directly.
        try:
            visible_data = self.state.profile
        except Exception:
            return

        if visible_data is None:
            return

        self.enable()

        x, y = visible_data

        # Update the data values.
        if len(x) > 0:
            self.state.update_limits()
            # Normalize profile values to the [0:1] range based on limits
            if self._viewer_state.normalize:
                y = self.state.normalize_values(y)
            with self.line_mark.hold_sync():
                self.line_mark.x = x
                self.line_mark.y = y
        else:
            with self.line_mark.hold_sync():
                self.line_mark.x = [0.]
                self.line_mark.y = [0.]

        if not self._viewer_state.normalize and len(y) > 0:

            y_min = nanmin(y)
            y_max = nanmax(y)
            y_range = y_max - y_min

            self.state._y_min = y_min - y_range * 0.1
            self.state._y_max = y_max + y_range * 0.1

            largest_y_max = max(getattr(layer, '_y_max', 0)
                                for layer in self._viewer_state.layers)
            if largest_y_max != self._viewer_state.y_max:
                self._viewer_state.y_max = largest_y_max

            smallest_y_min = min(getattr(layer, '_y_min', np.inf)
                                 for layer in self._viewer_state.layers)
            if smallest_y_min != self._viewer_state.y_min:
                self._viewer_state.y_min = smallest_y_min

        self.redraw()

    def _calculate_profile_error(self, exc):
        self.line_mark.visible = False
        self.redraw()
        if issubclass(exc[0], IncompatibleAttribute):
            if isinstance(self.state.layer, BaseData):
                self.disable_invalid_attributes(self.state.attribute)
            else:
                self.disable_incompatible_subset()
        elif issubclass(exc[0], IncompatibleDataException):
            self.disable("Incompatible data")

    def _update_visual_attributes(self):

        if not self.enabled:
            return

        self.line_mark.visible = self.state.visible
        self.line_mark.stroke_width = self.state.linewidth

        self.redraw()

    def _update_profile(self, force=False, **kwargs):

        # TODO: we need to factor the following code into a common method.

        if (self.line_mark is None or
                self._viewer_state.x_att is None or
                self.state.attribute is None or
                self.state.layer is None):
            return

        changed = set() if force else self.pop_changed_properties()

        if force or any(prop in changed for prop in ('layer', 'x_att', 'attribute',
                                                     'function', 'normalize',
                                                     'v_min', 'v_max')):
            self._calculate_profile(reset=force)
            force = True

        if force or any(prop in changed for prop in ('alpha', 'color', 'zorder',
                                                     'visible', 'linewidth')):
            self._update_visual_attributes()

    @defer_draw
    def update(self):
        self.state.reset_cache()
        self._update_profile(force=True)
        self.redraw()
