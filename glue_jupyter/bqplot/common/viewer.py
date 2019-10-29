import bqplot

from glue.core.subset import roi_to_subset_state
from glue.core.command import ApplySubsetState

from ...view import IPyWidgetView
from ...link import link, on_change
from ...utils import float_or_none

__all__ = ['BqplotBaseView']


class BqplotBaseView(IPyWidgetView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    is2d = True

    def __init__(self, session, state=None):

        # if we allow padding, we sometimes get odd behaviour with the interacts
        self.scale_x = bqplot.LinearScale(min=0, max=1, allow_padding=False)
        self.scale_y = bqplot.LinearScale(min=0, max=1)

        super(BqplotBaseView, self).__init__(session, state=state)

        self.scales = {'x': self.scale_x, 'y': self.scale_y}
        self.axis_x = bqplot.Axis(
            scale=self.scale_x, grid_lines='none', label='x')
        self.axis_y = bqplot.Axis(scale=self.scale_y, orientation='vertical', tick_format='0.2f',
                                  grid_lines='none', label='y')

        def update_axes(*ignore):
            self.axis_x.label = str(self.state.x_att)
            if self.is2d:
                self.axis_y.label = str(self.state.y_att)

        self.state.add_callback('x_att', update_axes)
        if self.is2d:
            self.state.add_callback('y_att', update_axes)
        self.figure = bqplot.Figure(scales=self.scales, animation_duration=0,
                                    axes=[self.axis_x, self.axis_y],
                                    fig_margin={'left': 60, 'bottom': 60, 'top': 10, 'right': 10})
        self.figure.padding_y = 0
        self._fig_margin_default = self.figure.fig_margin
        self._fig_margin_zero = dict(self.figure.fig_margin)
        self._fig_margin_zero['left'] = 0
        self._fig_margin_zero['bottom'] = 0

        link((self.state, 'x_min'), (self.scale_x, 'min'), float_or_none)
        link((self.state, 'x_max'), (self.scale_x, 'max'), float_or_none)
        link((self.state, 'y_min'), (self.scale_y, 'min'), float_or_none)
        link((self.state, 'y_max'), (self.scale_y, 'max'), float_or_none)

        on_change([(self.state, 'show_axes')])(self._sync_show_axes)

        self.create_layout()

    @property
    def figure_widget(self):
        return self.figure

    def _sync_show_axes(self):
        # TODO: if moved to state, this would not rely on the widget
        self.axis_x.visible = self.axis_y.visible = self.state.show_axes
        self.figure.fig_margin = (self._fig_margin_default if self.state.show_axes
                                  else self._fig_margin_zero)

    def apply_roi(self, roi, use_current=False):
        # TODO: partial copy paste from glue/viewers/matplotlib/qt/data_viewer.py
        with self._output_widget:
            if len(self.layers) > 0:
                subset_state = self._roi_to_subset_state(roi)
                cmd = ApplySubsetState(data_collection=self._data,
                                       subset_state=subset_state,
                                       use_current=use_current)
                self._session.command_stack.do(cmd)

    def _roi_to_subset_state(self, roi):
        # TODO: copy paste from glue/viewers/image/qt/data_viewer.py#L66

        # next lines don't work.. comp has no datetime?
        # x_date = any(comp.datetime for comp in self.state._get_x_components())
        # y_date = any(comp.datetime for comp in self.state._get_y_components())

        # if x_date or y_date:
        #    roi = roi.transformed(xfunc=mpl_to_datetime64 if x_date else None,
        #                          yfunc=mpl_to_datetime64 if y_date else None)
        if self.is2d:
            return roi_to_subset_state(roi, x_att=self.state.x_att, y_att=self.state.y_att)

    def limits_to_scales(self, *args):
        if self.state.x_min is not None and self.state.x_max is not None:
            self.scale_x.min = float(self.state.x_min)
            self.scale_x.max = float(self.state.x_max)

        if self.state.y_min is not None and self.state.y_max is not None:
            self.scale_y.min = float(self.state.y_min)
            self.scale_y.max = float(self.state.y_max)

    def redraw(self):
        pass
