from __future__ import absolute_import, division, print_function

from glue.viewers.scatter.layer_artist import ScatterLayerArtist
from glue.viewers.scatter.state import ScatterViewerState
from glue.viewers.scatter.viewer import MatplotlibScatterMixin

from .base import MatplotlibJupyterViewer

__all__ = ['ScatterJupyterViewer']


class ScatterJupyterViewer(MatplotlibJupyterViewer, MatplotlibScatterMixin):

    LABEL = '1D Scatter'

    _state_cls = ScatterViewerState
    _data_artist_cls = ScatterLayerArtist
    _subset_artist_cls = ScatterLayerArtist

    large_data_size = 2e7

    tools = ['select:xrange']

    def __init__(self, session, parent=None, state=None):
        super(ScatterJupyterViewer, self).__init__(session, parent=parent, state=state)
        MatplotlibScatterMixin.setup_callbacks(self)
