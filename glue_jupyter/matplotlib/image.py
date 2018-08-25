from __future__ import absolute_import, division, print_function

from glue.viewers.image.layer_artist import ImageLayerArtist
from glue.viewers.image.state import ImageViewerState
from glue.viewers.image.viewer import MatplotlibImageMixin

from .base import MatplotlibJupyterViewer

__all__ = ['ImageJupyterViewer']


class ImageJupyterViewer(MatplotlibJupyterViewer, MatplotlibImageMixin):

    LABEL = '1D Image'

    _state_cls = ImageViewerState
    _data_artist_cls = ImageLayerArtist
    _subset_artist_cls = ImageLayerArtist

    large_data_size = 2e7

    tools = ['select:xrange']

    def __init__(self, session, parent=None, state=None):
        super(ImageJupyterViewer, self).__init__(session, wcs=True, parent=parent, state=state)
        MatplotlibImageMixin.setup_callbacks(self)
