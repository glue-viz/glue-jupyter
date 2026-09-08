from __future__ import absolute_import, division, print_function

import sys
import warnings
import numpy as np

from glue.core import BaseData
from glue.utils import defer_draw, color2hex
from glue.viewers.profile.state import ProfileLayerState
from glue.core.exceptions import IncompatibleAttribute, IncompatibleDataException

import bqplot
from bqplot_image_gl import LinesGL

from glue.viewers.common.layer_artist import LayerArtist

from ...link import dlink

__all__ = ['BqplotProfileLayerArtist']


USE_GL = True


def values_to_nan_separated_lines(values):
    """
    Construct x and y arrays for a single ``Lines`` mark that renders one
    vertical line per value, using NaN values to separate the individual
    lines. The coordinate along the lines is 0 to 1, to be used with a [0:1]
    scale that is independent of the axes limits.
    """
    across = np.repeat(values.astype(np.float32), 3)
    across[2::3] = np.nan
    along = np.full(len(values) * 3, np.nan, dtype=np.float32)
    along[::3] = 0
    along[1::3] = 1
    return across, along


class BqplotProfileLayerArtist(LayerArtist):

    _layer_state_cls = ProfileLayerState

    def __init__(self, view, viewer_state, layer_state=None, layer=None):

        super().__init__(viewer_state, layer_state=layer_state, layer=layer)

        # Watch for changes in the viewer state which would require the
        # layers to be redrawn
        self._viewer_state.add_global_callback(self._update_profile)
        self.state.add_global_callback(self._update_profile)

        self.view = view

        LinesClass = LinesGL if USE_GL else bqplot.Lines
        self.line_mark = LinesClass(scales=self.view.scales, x=[0, 1], y=[0, 1])

        # The vertical lines are all rendered as a single Lines mark, with NaN
        # values separating the individual lines. The scale for the direction
        # along the lines is an independent [0:1] scale so that the lines
        # always span the full height of the plot regardless of the axes
        # limits.

        self.scale_along_lines = bqplot.LinearScale(min=0, max=1)
        self.vline_mark = bqplot.Lines(scales=dict(self.view.scales,
                                                   y=self.scale_along_lines),
                                       x=[], y=[], visible=False)

        self.view.figure.marks = list(self.view.figure.marks) + [self.line_mark, self.vline_mark]

        for mark in (self.line_mark, self.vline_mark):
            dlink((self.state, 'color'), (mark, 'colors'), lambda x: [color2hex(x)])
            dlink((self.state, 'alpha'), (mark, 'opacities'), lambda x: [x])
            mark.colors = [color2hex(self.state.color)]
            mark.opacities = [self.state.alpha]

    def remove(self):
        marks = self.view.figure.marks[:]
        marks.remove(self.line_mark)
        self.line_mark = None
        marks.remove(self.vline_mark)
        self.vline_mark = None
        self.view.figure.marks = marks
        return super().remove()

    def _update_positions(self):
        try:
            positions = self.state.compute_line_positions()
        except (IncompatibleAttribute, IndexError):
            with self.vline_mark.hold_sync():
                self.vline_mark.x = []
                self.vline_mark.y = []
            self.redraw()
            self.disable_invalid_attributes(self._viewer_state.x_att)
            return
        self.enable()
        with self.vline_mark.hold_sync():
            self.vline_mark.x, self.vline_mark.y = values_to_nan_separated_lines(positions)
        self.redraw()

    def _calculate_profile(self, reset=False):
        if self.state.display_mode == 'Vertical lines':
            self._update_positions()
            return
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
        if self.state.as_steps and len(x) > 0:
            a = np.insert(x, 0, 2*x[0] - x[1])
            b = np.append(x, 2*x[-1] - x[-2])
            edges = (a + b) / 2
            x = np.concatenate((edges[:1], np.repeat(edges[1:-1], 2), edges[-1:]))
            y = np.repeat(y, 2)

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

        self.redraw()

    def _calculate_profile_error(self, exc):
        self.line_mark.visible = False
        if issubclass(exc[0], (IncompatibleAttribute, IncompatibleDataException)):
            # If the profile cannot be computed but the position values along
            # the x axis can be resolved, the only way to show the layer is as
            # vertical lines, so we switch to that mode rather than disabling
            # the layer (which would also hide the layer options, making it
            # impossible to switch mode). Disabling only happens if neither
            # the profile nor the positions are available.
            try:
                self.state.compute_line_positions()
            except (IncompatibleAttribute, IndexError):
                pass
            else:
                if self.state.display_mode != 'Vertical lines':
                    # Changing the display mode retriggers an update, which
                    # will render the positions.
                    self.state.display_mode = 'Vertical lines'
                return
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

        # The profile and the vertical lines are alternative representations
        # of the layer, so only one of the two is ever visible.
        vline_mode = self.state.display_mode == 'Vertical lines'
        self.line_mark.visible = self.state.visible and not vline_mode
        self.line_mark.stroke_width = self.state.linewidth

        self.vline_mark.visible = self.state.visible and vline_mode
        self.vline_mark.stroke_width = self.state.linewidth

        self.redraw()

    def _update_profile(self, force=False, **kwargs):

        # TODO: we need to factor the following code into a common method.

        if (self.line_mark is None or
                self._viewer_state.x_att is None or
                self.state.layer is None or
                (self.state.attribute is None and self.state.display_mode != 'Vertical lines')):
            return

        # NOTE: we need to evaluate this even if force=True so that the cache
        # of updated properties is up to date after this method has been called.
        changed = self.pop_changed_properties()

        if force or any(prop in changed for prop in ('layer', 'x_att', 'attribute',
                                                     'function', 'normalize',
                                                     'v_min', 'v_max',
                                                     'as_steps',
                                                     'x_display_unit', 'y_display_unit',
                                                     'display_mode')):
            self._calculate_profile(reset=force)
            force = True

        if force or any(prop in changed for prop in ('alpha', 'color', 'zorder',
                                                     'visible', 'linewidth',
                                                     'display_mode')):
            self._update_visual_attributes()

    @defer_draw
    def update(self):
        self.state.reset_cache()
        self._update_profile(force=True)
        self.redraw()
