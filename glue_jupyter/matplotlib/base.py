from __future__ import absolute_import, division, print_function

import numpy as np

from matplotlib.patches import Rectangle
from matplotlib.backends.backend_nbagg import FigureCanvasNbAgg, FigureManager
from matplotlib.figure import Figure

from glue.viewers.common.viewer import Viewer
from glue.viewers.matplotlib.mpl_axes import init_mpl, update_appearance_from_settings
from glue.external.echo import delay_callback
from glue.utils import defer_draw, mpl_to_datetime64, avoid_circular, decorate_all_methods
from glue.viewers.matplotlib.state import MatplotlibDataViewerState

__all__ = ['MatplotlibJupyterViewer']

ZORDER_MAX = 100000

# FIXME: a lot of the code in this file is in common with the Qt code


@decorate_all_methods(defer_draw)
class MatplotlibJupyterViewer(Viewer):

    _state_cls = MatplotlibDataViewerState

    # tools = ['mpl:home', 'mpl:pan', 'mpl:zoom']
    # subtools = {'save': ['mpl:save']}

    large_data_size = None

    def __init__(self, session, parent=None, wcs=None, state=None):

        super(MatplotlibJupyterViewer, self).__init__(session, state=state)

        self.figure = Figure()
        self.canvas = FigureCanvasNbAgg(self.figure)
        self.canvas.manager = FigureManager(self.canvas, 0)

        self.figure, self.axes = init_mpl(self.figure, wcs=wcs)

        for spine in self.axes.spines.values():
            spine.set_zorder(ZORDER_MAX)

        self.loading_rectangle = Rectangle((0, 0), 1, 1, color='0.9', alpha=0.9,
                                           zorder=ZORDER_MAX - 1, transform=self.axes.transAxes)
        self.loading_rectangle.set_visible(False)
        self.axes.add_patch(self.loading_rectangle)

        self.loading_text = self.axes.text(0.4, 0.5, 'Computing', color='k',
                                           zorder=self.loading_rectangle.get_zorder() + 1,
                                           ha='left', va='center',
                                           transform=self.axes.transAxes)
        self.loading_text.set_visible(False)

        self.state.add_callback('aspect', self.update_aspect)

        self.update_aspect()

        self.state.add_callback('x_min', self.limits_to_mpl)
        self.state.add_callback('x_max', self.limits_to_mpl)
        self.state.add_callback('y_min', self.limits_to_mpl)
        self.state.add_callback('y_max', self.limits_to_mpl)

        self.limits_to_mpl()

        self.state.add_callback('x_log', self.update_x_log, priority=1000)
        self.state.add_callback('y_log', self.update_y_log, priority=1000)

        self.update_x_log()

        self.axes.callbacks.connect('xlim_changed', self.limits_from_mpl)
        self.axes.callbacks.connect('ylim_changed', self.limits_from_mpl)

        self.axes.set_autoscale_on(False)

        self.state.add_callback('x_axislabel', self.update_x_axislabel)
        self.state.add_callback('x_axislabel_weight', self.update_x_axislabel)
        self.state.add_callback('x_axislabel_size', self.update_x_axislabel)

        self.state.add_callback('y_axislabel', self.update_y_axislabel)
        self.state.add_callback('y_axislabel_weight', self.update_y_axislabel)
        self.state.add_callback('y_axislabel_size', self.update_y_axislabel)

        self.state.add_callback('x_ticklabel_size', self.update_x_ticklabel)
        self.state.add_callback('y_ticklabel_size', self.update_y_ticklabel)

        self.update_x_axislabel()
        self.update_y_axislabel()
        self.update_x_ticklabel()
        self.update_y_ticklabel()

    def _update_computation(self, message=None):
        pass

    def redraw(self):
        self.canvas.draw()

    def update_x_axislabel(self, *event):
        self.axes.set_xlabel(self.state.x_axislabel,
                             weight=self.state.x_axislabel_weight,
                             size=self.state.x_axislabel_size)
        self.redraw()

    def update_y_axislabel(self, *event):
        self.axes.set_ylabel(self.state.y_axislabel,
                             weight=self.state.y_axislabel_weight,
                             size=self.state.y_axislabel_size)
        self.redraw()

    def update_x_ticklabel(self, *event):
        self.axes.tick_params(axis='x', labelsize=self.state.x_ticklabel_size)
        self.axes.xaxis.get_offset_text().set_fontsize(self.state.x_ticklabel_size)
        self.redraw()

    def update_y_ticklabel(self, *event):
        self.axes.tick_params(axis='y', labelsize=self.state.y_ticklabel_size)
        self.axes.yaxis.get_offset_text().set_fontsize(self.state.y_ticklabel_size)
        self.redraw()

    def redraw(self):
        self.figure.canvas.draw()

    def update_x_log(self, *args):
        self.axes.set_xscale('log' if self.state.x_log else 'linear')
        self.redraw()

    def update_y_log(self, *args):
        self.axes.set_yscale('log' if self.state.y_log else 'linear')
        self.redraw()

    def update_aspect(self, aspect=None):
        self.axes.set_aspect(self.state.aspect, adjustable='datalim')

    @avoid_circular
    def limits_from_mpl(self, *args):

        with delay_callback(self.state, 'x_min', 'x_max', 'y_min', 'y_max'):

            if isinstance(self.state.x_min, np.datetime64):
                x_min, x_max = [mpl_to_datetime64(x) for x in self.axes.get_xlim()]
            else:
                x_min, x_max = self.axes.get_xlim()

            self.state.x_min, self.state.x_max = x_min, x_max

            if isinstance(self.state.y_min, np.datetime64):
                y_min, y_max = [mpl_to_datetime64(y) for y in self.axes.get_ylim()]
            else:
                y_min, y_max = self.axes.get_ylim()

            self.state.y_min, self.state.y_max = y_min, y_max

    @avoid_circular
    def limits_to_mpl(self, *args):

        if self.state.x_min is not None and self.state.x_max is not None:
            x_min, x_max = self.state.x_min, self.state.x_max
            if self.state.x_log:
                if self.state.x_max <= 0:
                    x_min, x_max = 0.1, 1
                elif self.state.x_min <= 0:
                    x_min = x_max / 10
            self.axes.set_xlim(x_min, x_max)

        if self.state.y_min is not None and self.state.y_max is not None:
            y_min, y_max = self.state.y_min, self.state.y_max
            if self.state.y_log:
                if self.state.y_max <= 0:
                    y_min, y_max = 0.1, 1
                elif self.state.y_min <= 0:
                    y_min = y_max / 10
            self.axes.set_ylim(y_min, y_max)

        if self.state.aspect == 'equal':

            # FIXME: for a reason I don't quite understand, dataLim doesn't
            # get updated immediately here, which means that there are then
            # issues in the first draw of the image (the limits are such that
            # only part of the image is shown). We just set dataLim manually
            # to avoid this issue.
            self.axes.dataLim.intervalx = self.axes.get_xlim()
            self.axes.dataLim.intervaly = self.axes.get_ylim()

            # We then force the aspect to be computed straight away
            self.axes.apply_aspect()

            # And propagate any changes back to the state since we have the
            # @avoid_circular decorator
            with delay_callback(self.state, 'x_min', 'x_max', 'y_min', 'y_max'):
                # TODO: fix case with datetime64 here
                self.state.x_min, self.state.x_max = self.axes.get_xlim()
                self.state.y_min, self.state.y_max = self.axes.get_ylim()

        self.redraw()

    def _update_appearance_from_settings(self, message=None):
        update_appearance_from_settings(self.axes)
        self.redraw()

    def get_layer_artist(self, cls, layer=None, layer_state=None):
        return cls(self.axes, self.state, layer=layer, layer_state=layer_state)

    def apply_roi(self, roi, override_mode=None):
        """ This method must be implemented by subclasses """
        raise NotImplementedError

    def show(self):
        self.canvas.manager.show()
