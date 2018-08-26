from __future__ import absolute_import, division, print_function

from glue.utils import defer_draw, decorate_all_methods
from glue.viewers.profile.layer_artist import ProfileLayerArtist
from glue.viewers.profile.state import ProfileViewerState
from glue.viewers.profile.viewer import MatplotlibProfileMixin

from .base import MatplotlibJupyterViewer

__all__ = ['ProfileJupyterViewer']


@decorate_all_methods(defer_draw)
class ProfileJupyterViewer(MatplotlibProfileMixin, MatplotlibJupyterViewer):

    LABEL = '1D Profile'

    _state_cls = ProfileViewerState
    _data_artist_cls = ProfileLayerArtist
    _subset_artist_cls = ProfileLayerArtist

    def __init__(self, session, parent=None, state=None):
        super(ProfileJupyterViewer, self).__init__(session, parent=parent, state=state)
        MatplotlibProfileMixin.setup_callbacks(self)
