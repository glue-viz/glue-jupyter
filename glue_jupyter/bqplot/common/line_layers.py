import numpy as np

import bqplot

from glue.core import BaseData
from glue.core.exceptions import IncompatibleAttribute
from glue.utils import color2hex
from glue.viewers.common.layer_artist import LayerArtist
from glue.viewers.common.line_layers import (LineLayerState, BaseLineLayerArtist,
                                             add_line_layer)

from ...link import dlink

__all__ = ['BqplotVerticalLineLayerArtist', 'BqplotHorizontalLineLayerArtist',
           'add_vertical_lines', 'add_horizontal_lines']


LINESTYLE_TO_BQPLOT = {'solid': 'solid',
                       'dashed': 'dashed',
                       'dotted': 'dotted',
                       'dashdot': 'dash_dotted'}


def values_to_nan_separated_lines(values):
    """
    Construct across and along arrays for a single ``Lines`` mark that
    renders one line per value, using NaN values to separate the individual
    lines. The coordinate along the lines is 0 to 1, to be used with a [0:1]
    scale that is independent of the axes limits.
    """
    across = np.repeat(values.astype(np.float32), 3)
    across[2::3] = np.nan
    along = np.full(len(values) * 3, np.nan, dtype=np.float32)
    along[::3] = 0
    along[1::3] = 1
    return across, along


class BqplotLineLayerArtist(LayerArtist, BaseLineLayerArtist):
    """
    A layer artist that renders the values of one of the viewer axis
    attributes for the layer as lines spanning the full extent of the other
    axis.

    All the lines are rendered as a single ``Lines`` mark with NaN values
    separating the individual lines, so that this stays efficient even for
    many thousands of lines.
    """

    _layer_state_cls = LineLayerState

    def __init__(self, view, viewer_state, layer_state=None, layer=None):

        super(BqplotLineLayerArtist, self).__init__(viewer_state,
                                                    layer_state=layer_state,
                                                    layer=layer)

        self.view = view

        self._viewer_state.add_global_callback(self._update_line_layer)
        self.state.add_global_callback(self._update_line_layer)

        # The scale for the direction along the lines is an independent [0:1]
        # scale so that the lines always span the full extent of the plot
        # regardless of the axes limits.
        self.scale_along_lines = bqplot.LinearScale(min=0, max=1)
        scales = dict(self.view.scales)
        if self._orientation == 'horizontal':
            scales['x'] = self.scale_along_lines
        else:
            scales['y'] = self.scale_along_lines
        self.line_mark = bqplot.Lines(scales=scales, x=[], y=[], visible=False)

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

    def _update_data(self):

        try:
            positions = self.compute_line_positions()
        except (IncompatibleAttribute, IndexError):
            with self.line_mark.hold_sync():
                self.line_mark.x = []
                self.line_mark.y = []
            self.redraw()
            if isinstance(self.state.layer, BaseData):
                self.disable_invalid_attributes(self._position_att)
            else:
                self.disable_incompatible_subset()
            return

        self.enable()
        across, along = values_to_nan_separated_lines(positions)
        with self.line_mark.hold_sync():
            if self._orientation == 'horizontal':
                self.line_mark.x, self.line_mark.y = along, across
            else:
                self.line_mark.x, self.line_mark.y = across, along
        self.redraw()

    def _update_visual_attributes(self):

        if not self.enabled:
            return

        self.line_mark.visible = self.state.visible
        self.line_mark.stroke_width = self.state.linewidth
        self.line_mark.line_style = LINESTYLE_TO_BQPLOT[self.state.linestyle]

        self.redraw()

    def _update_line_layer(self, force=False, **kwargs):

        if (self.line_mark is None or
                self._position_att is None or
                self.state.layer is None):
            return

        # NOTE: we need to evaluate this even if force=True so that the cache
        # of updated properties is up to date after this method has been called.
        changed = self.pop_changed_properties()

        if force or self._changed_position_properties(changed):
            self._update_data()
            force = True

        if force or any(prop in changed for prop in ('alpha', 'color', 'zorder', 'visible',
                                                     'linewidth', 'linestyle')):
            self._update_visual_attributes()

    def update(self):
        self._update_line_layer(force=True)
        self.redraw()


class BqplotVerticalLineLayerArtist(BqplotLineLayerArtist):
    """
    A layer artist that renders the values of the viewer x attribute for the
    layer as full-height vertical lines, for use in any bqplot viewer whose
    viewer state has an ``x_att`` attribute, e.g. the scatter, profile,
    histogram, and image viewers.
    """

    _orientation = 'vertical'


class BqplotHorizontalLineLayerArtist(BqplotLineLayerArtist):
    """
    A layer artist that renders the values of the viewer y attribute for the
    layer as full-width horizontal lines, for use in any bqplot viewer whose
    viewer state has a ``y_att`` attribute, e.g. the scatter and image
    viewers.
    """

    _orientation = 'horizontal'


def add_vertical_lines(viewer, layer):
    """
    Add a dataset or subset to a bqplot-based viewer as full-height vertical
    lines at the values of the viewer x attribute.

    Any existing subsets of a dataset are added along with it, and any
    subsets created afterwards will also be shown as vertical lines.
    """
    return add_line_layer(viewer, layer, BqplotVerticalLineLayerArtist)


def add_horizontal_lines(viewer, layer):
    """
    Add a dataset or subset to a bqplot-based viewer as full-width horizontal
    lines at the values of the viewer y attribute.

    Any existing subsets of a dataset are added along with it, and any
    subsets created afterwards will also be shown as horizontal lines.
    """
    return add_line_layer(viewer, layer, BqplotHorizontalLineLayerArtist)
