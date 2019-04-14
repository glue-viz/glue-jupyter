from __future__ import absolute_import, division, print_function

from ipywidgets import Tab, HBox, VBox, Output
from IPython.display import display

# from matplotlib.backends.backend_nbagg import FigureCanvasNbAgg, FigureManager
from ipympl.backend_nbagg import FigureCanvasNbAgg, FigureManagerNbAgg
from matplotlib.figure import Figure

from glue.viewers.matplotlib.mpl_axes import init_mpl
from glue.viewers.matplotlib.state import MatplotlibDataViewerState
from glue.viewers.matplotlib.viewer import MatplotlibViewerMixin

from glue_jupyter.view import IPyWidgetView

__all__ = ['MatplotlibJupyterViewer']


class MatplotlibJupyterViewer(MatplotlibViewerMixin, IPyWidgetView):

    _state_cls = MatplotlibDataViewerState

    large_data_size = None

    def __init__(self, session, parent=None, wcs=None, state=None):

        super(MatplotlibJupyterViewer, self).__init__(session, state=state)

        self.figure = Figure()
        self.canvas = FigureCanvasNbAgg(self.figure)
        self.canvas.manager = FigureManagerNbAgg(self.canvas, 0)

        self.figure, self.axes = init_mpl(self.figure, wcs=wcs)

        MatplotlibViewerMixin.setup_callbacks(self)

        self.create_tab()
        self.output_widget = Output()

        self.main_widget = VBox([
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
