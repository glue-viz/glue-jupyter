from typing import Dict, Type
from functools import partial

import bqplot
import react_ipywidgets as react
import react_ipywidgets.bqplot as bq
from bqplot_image_gl.interacts import MouseInteraction
from echo.callback_container import CallbackContainer
from glue.core.command import ApplySubsetState
from glue.core.subset import roi_to_subset_state
from glue.viewers.common.state import State
from glue.viewers.histogram.state import HistogramViewerState
from bqplot_image_gl.interacts import MouseInteraction, keyboard_events, mouse_events

from ...common.hooks import use_echo_state, use_layer_watch

from ...view import IPyWidgetView
from .tools import ROIClickAndDrag



def create_scale(viewer_state, name):
    is_log, set_x_log = use_echo_state(viewer_state, f"{name}_log")
    v_min, set_v_min = use_echo_state(viewer_state, f"{name}_min")
    v_max, set_v_max = use_echo_state(viewer_state, f"{name}_max")
    if is_log:
        scale = bq.LogScale(min=v_min, max=v_max, allow_padding=False)
    else:
        scale = bq.LinearScale(min=v_min, max=v_max, allow_padding=False)
    return scale


@react.component
def Figure(
    viewer: IPyWidgetView,
    viewer_state,
    is2d,
    components: Dict[Type[State], react.core.Component],
):
    use_layer_watch(viewer)  # will simply trigger when the layers change

    scale_x = create_scale(viewer_state, "x")
    scale_y = create_scale(viewer_state, "y")

    x_att, _ = use_echo_state(viewer_state, "x_att")
    try:
        # Extract units from data
        x_unit = viewer_state.reference_data.get_component(
            viewer_state.x_att_world
        ).units
    except AttributeError:
        # If no data loaded yet, ignore units
        x_unit = ""
    finally:
        # Append units to axis label
        label_x = str(x_att) + " " + str(x_unit)

    if is2d:  # use is conditional, which is ok because is2d will not change
        y_att, _ = use_echo_state(viewer_state, "y_att")
        label_y = str(y_att)
        try:
            y_unit = viewer_state.reference_data.get_component(
                viewer_state.y_att_world
            ).units
        except AttributeError:
            y_unit = ""
        finally:
            label_y = str(y_att) + " " + str(y_unit)
    else:
        label_y = "no label"

    marks = [
        components[type(state)](scale_x, scale_y, viewer_state, state)
        for state in viewer_state.layers
        if not state.disabled
    ]

    show_axes, _ = use_echo_state(viewer_state, "show_axes")
    # print(viewer_state)
    axis_x = bq.Axis(scale=scale_x, grid_lines="none", label=label_x, visible=show_axes)
    axis_y = bq.Axis(
        scale=scale_y,
        orientation="vertical",
        tick_format="0.2f",
        grid_lines="none",
        label=label_y,
        visible=show_axes,
    )

    if show_axes:
        fig_margin = {"left": 60, "bottom": 60, "top": 10, "right": 10}
    else:
        fig_margin = {"left": 0, "bottom": 0, "top": 10, "right": 10}

    mouse_interact = MouseInteraction.element(
        x_scale=scale_x, y_scale=scale_y, move_throttle=70, events=[]
    )
    return bq.Figure(
        scale_x=scale_x,
        scale_y=scale_y,
        animation_duration=0,
        marks=marks,
        interaction=mouse_interact,
        axes=[axis_x, axis_y],
        fig_margin=fig_margin,
        padding_y=0,
    )


class BqplotBaseViewReact(IPyWidgetView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    is2d = True
    _default_mouse_mode_cls = ROIClickAndDrag

    def initialize_figure(self):
        self.figure_el = Figure(
            self, self.state, is2d=self.is2d, components=self.components
        )
        self._figure: bqplot.Figure = react.render_fixed(self.figure_el)[0]
        self.scale_x = self._figure.scale_x
        self.scale_y = self._figure.scale_y
        self.scales = {"x": self.scale_x, "y": self.scale_y}
        self._mouse_interact = self._figure.interaction
        # Set up a MouseInteraction instance here tied to the figure. In the
        # tools we then chain this with any other active interact so that we can
        # always listen for certain events. This allows us to then have e.g.
        # mouse-over coordinates regardless of whether tools are active or not.
        self._event_callbacks = CallbackContainer()
        self._events_for_callback = {}

    @property
    def figure_widget(self):
        return self._figure

    def apply_roi(self, roi, use_current=False):
        # TODO: partial copy paste from glue/viewers/matplotlib/qt/data_viewer.py
        # with self._output_widget:
        
            if len(self.layers) > 0:
                subset_state = self._roi_to_subset_state(roi)
                cmd = ApplySubsetState(
                    data_collection=self._data,
                    subset_state=subset_state,
                    override_mode=use_current,
                )
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
            return roi_to_subset_state(
                roi, x_att=self.state.x_att, y_att=self.state.y_att
            )


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

    def _callback_key(self, callback):
        if CallbackContainer.is_bound_method(callback):
            return (callback.__func__, (callback.__self__,))
        elif isinstance(callback, partial):
            return (callback.func, callback.args)
        return callback