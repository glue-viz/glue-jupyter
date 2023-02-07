import bqplot
from functools import partial
from contextlib import nullcontext

from glue.core.subset import roi_to_subset_state
from glue.core.command import ApplySubsetState

from bqplot_image_gl.interacts import MouseInteraction, keyboard_events, mouse_events

from echo.callback_container import CallbackContainer

from ...view import IPyWidgetView
from ...link import on_change
from ...utils import debounced, get_ioloop
from .tools import ROIClickAndDrag

__all__ = ['BqplotBaseView']


class BqplotBaseView(IPyWidgetView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    is2d = True
    _default_mouse_mode_cls = ROIClickAndDrag

    def __init__(self, session, state=None):

        # if we allow padding, we sometimes get odd behaviour with the interacts
        self.scale_x = bqplot.LinearScale(min=0, max=1, allow_padding=False)
        self.scale_y = bqplot.LinearScale(min=0, max=1)

        self.scales = {'x': self.scale_x, 'y': self.scale_y}
        self.axis_x = bqplot.Axis(
            scale=self.scale_x, grid_lines='none', label='x')
        self.axis_y = bqplot.Axis(scale=self.scale_y, orientation='vertical', tick_format='0.2f',
                                  grid_lines='none', label='y')

        self.figure = bqplot.Figure(scale_x=self.scale_x, scale_y=self.scale_y,
                                    animation_duration=0,
                                    axes=[self.axis_x, self.axis_y],
                                    fig_margin={'left': 60, 'bottom': 60, 'top': 10, 'right': 10})
        self.figure.padding_y = 0
        self._fig_margin_default = self.figure.fig_margin
        self._fig_margin_zero = dict(self.figure.fig_margin)
        self._fig_margin_zero['left'] = 0
        self._fig_margin_zero['bottom'] = 0

        # Set up a MouseInteraction instance here tied to the figure. In the
        # tools we then chain this with any other active interact so that we can
        # always listen for certain events. This allows us to then have e.g.
        # mouse-over coordinates regardless of whether tools are active or not.
        self._event_callbacks = CallbackContainer()
        self._mouse_interact = MouseInteraction(x_scale=self.scale_x,
                                                y_scale=self.scale_y,
                                                move_throttle=70,
                                                events=[])
        self._mouse_interact.on_msg(self._on_mouse_interaction)
        self.figure.interaction = self._mouse_interact
        self._events_for_callback = {}

        super(BqplotBaseView, self).__init__(session, state=state)

        # Remove the following two lines once glue v0.16 is required - see
        # https://github.com/glue-viz/glue/pull/2099/files for more information.
        self.state.remove_callback('layers', self._sync_layer_artist_container)
        self.state.add_callback('layers', self._sync_layer_artist_container, priority=10000)

        self.state.add_callback('x_axislabel', self.update_x_axislabel)
        # self.state.add_callback('x_axislabel_weight', self.update_x_axislabel)
        # self.state.add_callback('x_axislabel_size', self.update_x_axislabel)

        self.state.add_callback('y_axislabel', self.update_y_axislabel)
        # self.state.add_callback('y_axislabel_weight', self.update_y_axislabel)
        # self.state.add_callback('y_axislabel_size', self.update_y_axislabel)

        self.scale_x.observe(self.update_glue_scales, names=['min', 'max'])
        self.scale_y.observe(self.update_glue_scales, names=['min', 'max'])

        self._last_limits = None
        self.state.add_callback('x_min', self._update_bqplot_limits)
        self.state.add_callback('x_max', self._update_bqplot_limits)
        self.state.add_callback('y_min', self._update_bqplot_limits)
        self.state.add_callback('y_max', self._update_bqplot_limits)

        self._update_bqplot_limits()

        on_change([(self.state, 'show_axes')])(self._sync_show_axes)

        self.create_layout()

    def update_x_axislabel(self, *event):
        self.axis_x.label = self.state.x_axislabel

    def update_y_axislabel(self, *event):
        self.axis_y.label = self.state.y_axislabel

    def _update_bqplot_limits(self, *args):

        if self._last_limits == (self.state.x_min, self.state.x_max,
                                 self.state.y_min, self.state.y_max):
            return

        # NOTE: in the following, the figure will still update twice. There
        # isn't a way around it at the moment and nesting the context managers
        # doesn't change this - at the end of the day, the two scales are
        # separate widgets so will result in two updates.

        if self.state.x_min is not None and self.state.x_max is not None:
            with self.scale_x.hold_sync():
                self.scale_x.min = float(self.state.x_min)
                self.scale_x.max = float(self.state.x_max)

        if self.state.y_min is not None and self.state.y_max is not None:
            with self.scale_y.hold_sync():
                self.scale_y.min = float(self.state.y_min)
                self.scale_y.max = float(self.state.y_max)

        self._last_limits = (self.state.x_min, self.state.x_max,
                             self.state.y_min, self.state.y_max)

    def _callback_key(self, callback):
        if CallbackContainer.is_bound_method(callback):
            return (callback.__func__, (callback.__self__,))
        elif isinstance(callback, partial):
            return (callback.func, callback.args)
        return callback

    def add_event_callback(self, callback, events=None):
        """
        Add a callback function for mouse and keyboard events when the mouse is over the figure.

        Parameters
        ----------
        callback : func
            The callback function. This should take a single argument which is a
            dictionary containing the event details. One of the keys of the
            dictionary is ``event`` which is a string that describes the event
            (see the ``events`` parameter for possible strings). The rest of the
            dictionary depends on the specific event triggered.
        events : list, optional
            The list of events to listen for. The following events are available:

            * ``'click'``
            * ``'dblclick'``
            * ``'mouseenter'``
            * ``'mouseleave'``
            * ``'contextmenu'``
            * ``'mousemove'``
            * ``'keydown'``
            * ``'keyup'``

            If this parameter is not passed, all events will be listened for.
        """

        if events is None:
            events = keyboard_events + mouse_events

        self._event_callbacks.append(callback)
        key = self._callback_key(callback)
        self._events_for_callback[key] = set(events)
        self._update_interact_events()

    def remove_event_callback(self, callback):
        """
        Remove a callback function for mouse and keyboard events.
        """
        key = self._callback_key(callback)
        self._events_for_callback.pop(key)
        self._event_callbacks.remove(callback)
        self._update_interact_events()

    def _update_interact_events(self):
        events = set()
        for individual_events in self._events_for_callback.values():
            events |= individual_events
        events = sorted(events)
        self._mouse_interact.events = sorted(events)

    def _on_mouse_interaction(self, interaction, data, buffers):
        for callback in self._event_callbacks:
            key = self._callback_key(callback)
            events = self._events_for_callback.get(key, [])
            if data["event"] in events:
                callback(data)

    @debounced(delay_seconds=0.5, method=True)
    def update_glue_scales(self, *ignored):
        # To prevent glue from calling _adjust_limit_aspect() as each value comes in, we wait for
        # all values to be set and then update the glue-state atomically.
        #
        # If this is not done, the _adjust_limit_aspect() starts calculating with one of the new
        # values, which changes x_min, x_max, y_min and y_max, which gets synced to the front-end,
        # which causes another change resulting in a short feedback loop that ends with the values
        # being different than originally set.

        # In the unit tests @debounced does not work and will lead to unrelated failing tests. The
        # updating of glue-state to widgets isn't tested anyway, so skip this code when we don't
        # detect an ioloop.
        # TODO: come up with a better solution for this problem
        if get_ioloop():
            state = self.state.as_dict()
            state['x_min'] = self.scale_x.min
            state['x_max'] = self.scale_x.max
            state['y_min'] = self.scale_y.min
            state['y_max'] = self.scale_y.max
            self.state.update_from_dict(state)

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
        with self._output_widget or nullcontext():
            if len(self.layers) > 0:
                subset_state = self._roi_to_subset_state(roi)
                cmd = ApplySubsetState(data_collection=self._data,
                                       subset_state=subset_state,
                                       override_mode=use_current)
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
