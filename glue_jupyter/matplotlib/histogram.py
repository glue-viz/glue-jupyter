from __future__ import absolute_import, division, print_function

from glue.viewers.histogram.layer_artist import HistogramLayerArtist
from glue.viewers.histogram.state import HistogramViewerState
from glue.viewers.histogram.viewer import MatplotlibHistogramMixin

from .base import MatplotlibJupyterViewer

__all__ = ['HistogramJupyterViewer']


class HistogramJupyterViewer(MatplotlibJupyterViewer, MatplotlibHistogramMixin):

    LABEL = '1D Histogram'

    _state_cls = HistogramViewerState
    _data_artist_cls = HistogramLayerArtist
    _subset_artist_cls = HistogramLayerArtist

    large_data_size = 2e7

    tools = ['select:xrange']

    def __init__(self, session, parent=None, state=None):
        super(HistogramJupyterViewer, self).__init__(session, parent=parent, state=state)
        MatplotlibHistogramMixin.setup_callbacks(self)
