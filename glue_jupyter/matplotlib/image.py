from __future__ import absolute_import, division, print_function

from glue.utils import defer_draw, decorate_all_methods
from glue.viewers.image.layer_artist import ImageLayerArtist, ImageSubsetLayerArtist
from glue.viewers.scatter.layer_artist import ScatterLayerArtist
from glue.viewers.image.state import ImageViewerState
from glue.viewers.image.viewer import MatplotlibImageMixin

from .base import MatplotlibJupyterViewer

from glue_jupyter.common.state_widgets.layer_scatter import ScatterLayerStateWidget
from glue_jupyter.common.state_widgets.layer_image import (ImageLayerStateWidget,
                                                           ImageSubsetLayerStateWidget)
from glue_jupyter.common.state_widgets.viewer_image import ImageViewerStateWidget

__all__ = ['ImageJupyterViewer']


@decorate_all_methods(defer_draw)
class ImageJupyterViewer(MatplotlibImageMixin, MatplotlibJupyterViewer):

    LABEL = '2D Image'

    _state_cls = ImageViewerState
    _data_artist_cls = ImageLayerArtist
    _options_cls = ImageViewerStateWidget
    _subset_artist_cls = ImageLayerArtist
    _layer_style_widget_cls = {ImageLayerArtist: ImageLayerStateWidget,
                               ImageSubsetLayerArtist: ImageSubsetLayerStateWidget,
                               ScatterLayerArtist: ScatterLayerStateWidget}

    tools = ['select:rectangle', 'select:xrange',
             'select:yrange', 'select:circle',
             'select:polygon']

    def __init__(self, session, parent=None, state=None):
        super(ImageJupyterViewer, self).__init__(session, wcs=True, parent=parent, state=state)
        MatplotlibImageMixin.setup_callbacks(self)
