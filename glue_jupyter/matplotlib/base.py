from __future__ import absolute_import, division, print_function

from matplotlib.backends.backend_nbagg import FigureCanvasNbAgg, FigureManager
from matplotlib.figure import Figure

from glue.viewers.common.viewer import Viewer
from glue.viewers.matplotlib.mpl_axes import init_mpl
from glue.utils import defer_draw, decorate_all_methods
from glue.viewers.matplotlib.state import MatplotlibDataViewerState
from glue.viewers.matplotlib.viewer import MatplotlibMixin

__all__ = ['MatplotlibJupyterViewer']


@decorate_all_methods(defer_draw)
class MatplotlibJupyterViewer(MatplotlibMixin, Viewer):

    _state_cls = MatplotlibDataViewerState

    large_data_size = None

    def __init__(self, session, parent=None, wcs=None, state=None):

        super(MatplotlibJupyterViewer, self).__init__(session, state=state)

        self.figure = Figure()
        self.canvas = FigureCanvasNbAgg(self.figure)
        self.canvas.manager = FigureManager(self.canvas, 0)

        self.figure, self.axes = init_mpl(self.figure, wcs=wcs)

        MatplotlibMixin.setup_callbacks(self)

    def show(self):
        self.canvas.manager.show()
