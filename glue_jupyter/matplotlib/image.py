from __future__ import absolute_import, division, print_function

from glue.utils import defer_draw, decorate_all_methods
from glue.viewers.image.layer_artist import ImageLayerArtist
from glue.viewers.image.state import ImageViewerState
from glue.viewers.image.viewer import MatplotlibImageMixin

from .base import MatplotlibJupyterViewer

__all__ = ['ImageJupyterViewer']


@decorate_all_methods(defer_draw)
class ImageJupyterViewer(MatplotlibImageMixin, MatplotlibJupyterViewer):

    LABEL = '1D Image'

    _state_cls = ImageViewerState
    _data_artist_cls = ImageLayerArtist
    _subset_artist_cls = ImageLayerArtist

    large_data_size = 2e7

    def __init__(self, session, parent=None, state=None):
        super(ImageJupyterViewer, self).__init__(session, wcs=True, parent=parent, state=state)
        MatplotlibImageMixin.setup_callbacks(self)
