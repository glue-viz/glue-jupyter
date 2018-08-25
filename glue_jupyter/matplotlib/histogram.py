from __future__ import absolute_import, division, print_function

from glue.core.util import update_ticks
from glue.utils import defer_draw, decorate_all_methods

from glue.viewers.histogram.layer_artist import HistogramLayerArtist
from glue.viewers.histogram.state import HistogramViewerState

from .base import MatplotlibJupyterViewer

__all__ = ['HistogramJupyterViewer']


@decorate_all_methods(defer_draw)
class HistogramJupyterViewer(MatplotlibJupyterViewer):

    LABEL = '1D Histogram'
    _state_cls = HistogramViewerState
    _data_artist_cls = HistogramLayerArtist
    _subset_artist_cls = HistogramLayerArtist

    large_data_size = 2e7

    # FIXME: the remainder of the code in this file is in common with the
    # Qt Histogram class.

    def __init__(self, session, parent=None, state=None):
        super(HistogramJupyterViewer, self).__init__(session, parent, state=state)
        self.state.add_callback('x_att', self._update_axes)
        self.state.add_callback('x_log', self._update_axes)
        self.state.add_callback('normalize', self._update_axes)

    def _update_axes(self, *args):

        if self.state.x_att is not None:

            # Update ticks, which sets the labels to categories if components are categorical
            update_ticks(self.axes, 'x', self.state.x_kinds, self.state.x_log, self.state.x_categories)

            if self.state.x_log:
                self.state.x_axislabel = 'Log ' + self.state.x_att.label
            else:
                self.state.x_axislabel = self.state.x_att.label

        if self.state.normalize:
            self.state.y_axislabel = 'Normalized number'
        else:
            self.state.y_axislabel = 'Number'

        self.axes.figure.canvas.draw()
