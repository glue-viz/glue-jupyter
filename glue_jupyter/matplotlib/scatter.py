from __future__ import absolute_import, division, print_function

from glue.utils import defer_draw, decorate_all_methods
from glue.viewers.scatter.layer_artist import ScatterLayerArtist
from glue.viewers.scatter.state import ScatterViewerState
from glue.viewers.scatter.viewer import MatplotlibScatterMixin

from .base import MatplotlibJupyterViewer

from glue_jupyter.common.state_widgets.layer_scatter import ScatterLayerStateWidget
from glue_jupyter.common.state_widgets.viewer_scatter import ScatterViewerStateWidget

__all__ = ['ScatterJupyterViewer']


@decorate_all_methods(defer_draw)
class ScatterJupyterViewer(MatplotlibScatterMixin, MatplotlibJupyterViewer):

    LABEL = '2D Scatter'

    _state_cls = ScatterViewerState
    _data_artist_cls = ScatterLayerArtist
    _subset_artist_cls = ScatterLayerArtist
    _options_cls = ScatterViewerStateWidget
    _layer_style_widget_cls = ScatterLayerStateWidget

    tools = ['select:rectangle', 'select:xrange',
             'select:yrange', 'select:circle',
             'select:polygon']

    def __init__(self, session, parent=None, state=None):
        super(ScatterJupyterViewer, self).__init__(session, parent=parent, state=state)
        MatplotlibScatterMixin.setup_callbacks(self)
