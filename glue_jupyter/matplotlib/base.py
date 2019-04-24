from __future__ import absolute_import, division, print_function

from ipywidgets import HTML, Tab, HBox, VBox, Output
from IPython.display import display

from ipympl.backend_nbagg import FigureCanvasNbAgg, FigureManagerNbAgg
from matplotlib.figure import Figure

from glue.viewers.matplotlib.mpl_axes import init_mpl
from glue.viewers.matplotlib.state import MatplotlibDataViewerState
from glue.viewers.matplotlib.viewer import MatplotlibViewerMixin

from glue.utils.matplotlib import DEFER_DRAW_BACKENDS

from glue_jupyter.view import IPyWidgetView

__all__ = ['MatplotlibJupyterViewer']

# Register the Qt backend with defer_draw
DEFER_DRAW_BACKENDS.append(FigureCanvasNbAgg)

# By default, the Jupyter Matplotlib widget has a big clunky title bar, so
# we apply custom CSS to remove it.
REMOVE_TITLE_CSS = "<style> .output_wrapper .ui-dialog-titlebar { display: none; } </style>"


class MatplotlibJupyterViewer(MatplotlibViewerMixin, IPyWidgetView):

    _state_cls = MatplotlibDataViewerState

    large_data_size = None

    def __init__(self, session, parent=None, wcs=None, state=None):

        self.figure = Figure()
        self.canvas = FigureCanvasNbAgg(self.figure)
        self.canvas.manager = FigureManagerNbAgg(self.canvas, 0)
        self.figure, self.axes = init_mpl(self.figure, wcs=wcs)

        # FIXME: The following is required for now for the tools to work
        self.central_widget = self.figure
        self._axes = self.axes

        super(MatplotlibJupyterViewer, self).__init__(session, state=state)

        MatplotlibViewerMixin.setup_callbacks(self)

        self.create_tab()
        self.output_widget = Output()

        self.css_widget = HTML(REMOVE_TITLE_CSS)

        self.main_widget = VBox([
                self.css_widget,
                self.widget_toolbar,
                HBox([self.canvas, self.tab]),
                self.output_widget
            ])

    def show(self):
        display(self.main_widget)

    def get_layer_artist(self, cls, layer=None, layer_state=None):
        # TODO: this method should be defined on the base viewer class
        layer = super().get_layer_artist(cls, layer=layer, layer_state=layer_state)
        self._add_layer_tab(layer)
        return layer

    def create_tab(self):
        self.tab = Tab([self._options_cls(self.state)])
        self.tab.set_title(0, "General")
