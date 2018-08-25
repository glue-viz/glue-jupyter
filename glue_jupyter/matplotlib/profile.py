from __future__ import absolute_import, division, print_function

from glue.viewers.profile.layer_artist import ProfileLayerArtist
from glue.viewers.profile.state import ProfileViewerState
from glue.viewers.profile.viewer import MatplotlibProfileMixin

from .base import MatplotlibJupyterViewer

__all__ = ['ProfileJupyterViewer']


class ProfileJupyterViewer(MatplotlibJupyterViewer, MatplotlibProfileMixin):

    LABEL = '1D Profile'

    _state_cls = ProfileViewerState
    _data_artist_cls = ProfileLayerArtist
    _subset_artist_cls = ProfileLayerArtist

    large_data_size = 2e7

    tools = ['select:xrange']

    def __init__(self, session, parent=None, state=None):
        super(ProfileJupyterViewer, self).__init__(session, parent=parent, state=state)
        MatplotlibProfileMixin.setup_callbacks(self)
