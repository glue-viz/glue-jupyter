from __future__ import absolute_import, division, print_function

from glue.utils import defer_draw, decorate_all_methods
from glue.viewers.profile.layer_artist import ProfileLayerArtist
from glue.viewers.profile.state import ProfileViewerState
from glue.viewers.profile.viewer import MatplotlibProfileMixin

from .base import MatplotlibJupyterViewer

from glue_jupyter.common.state_widgets.layer_profile import ProfileLayerStateWidget
from glue_jupyter.common.state_widgets.viewer_profile import ProfileViewerStateWidget

__all__ = ['ProfileJupyterViewer']


@decorate_all_methods(defer_draw)
class ProfileJupyterViewer(MatplotlibProfileMixin, MatplotlibJupyterViewer):

    LABEL = '1D Profile'

    _state_cls = ProfileViewerState
    _data_artist_cls = ProfileLayerArtist
    _subset_artist_cls = ProfileLayerArtist
    _options_cls = ProfileViewerStateWidget
    _layer_style_widget_cls = ProfileLayerStateWidget

    def __init__(self, session, parent=None, state=None):
        super(ProfileJupyterViewer, self).__init__(session, parent=parent, state=state)
        MatplotlibProfileMixin.setup_callbacks(self)
