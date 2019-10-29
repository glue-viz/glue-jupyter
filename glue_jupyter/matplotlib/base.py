from __future__ import absolute_import, division, print_function

from ipywidgets import HTML, VBox

try:
    from ipympl.backend_nbagg import Canvas, FigureManager
except ImportError:  # Prior to June 2019
    from ipympl.backend_nbagg import (FigureCanvasNbAgg as Canvas,
                                      FigureManagerNbAgg as FigureManager)

from matplotlib.figure import Figure

from glue.viewers.matplotlib.mpl_axes import init_mpl
from glue.viewers.matplotlib.state import MatplotlibDataViewerState
from glue.viewers.matplotlib.viewer import MatplotlibViewerMixin

from glue.utils.matplotlib import DEFER_DRAW_BACKENDS

from glue_jupyter.view import IPyWidgetView

__all__ = ['MatplotlibJupyterViewer']

# Register the Qt backend with defer_draw
DEFER_DRAW_BACKENDS.append(Canvas)

# By default, the Jupyter Matplotlib widget has a big clunky title bar, so
# we apply custom CSS to remove it.
REMOVE_TITLE_CSS = "<style> .output_wrapper .ui-dialog-titlebar { display: none; } </style>"


class MatplotlibJupyterViewer(MatplotlibViewerMixin, IPyWidgetView):

    _state_cls = MatplotlibDataViewerState

    large_data_size = None

    def __init__(self, session, parent=None, wcs=None, state=None):

        self.figure = Figure()
        self.canvas = Canvas(self.figure)
        self.canvas.manager = FigureManager(self.canvas, 0)
        self.figure, self.axes = init_mpl(self.figure, wcs=wcs)

        # FIXME: The following is required for now for the tools to work
        self.central_widget = self.figure
        self._axes = self.axes

        super(MatplotlibJupyterViewer, self).__init__(session, state=state)

        MatplotlibViewerMixin.setup_callbacks(self)

        self.css_widget = HTML(REMOVE_TITLE_CSS)

        self.create_layout()

    @property
    def figure_widget(self):
        return VBox([self.css_widget, self.canvas])
