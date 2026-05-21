"""
PV slicer tool for the bqplot image viewer.

bqplot has no analogue of matplotlib's :class:`PathMode`, so this module
implements a small click-to-add-vertex / Enter-to-finalise tool on top
of the viewer's ``add_event_callback`` machinery. The data-side logic
(creating / updating :class:`PathSlicedData` and wiring the link graph)
is shared with the matplotlib variant via :mod:`.common`.
"""
import numpy as np

from bqplot import Lines, Scatter

from glue.config import viewer_tool

from glue_jupyter.bqplot.common.tools import (InteractCheckableTool,
                                              INTERACT_COLOR)
from glue_jupyter.bqplot.image import BqplotImageView

from .common import build_or_update_pvs, drive_parent_slice


__all__ = ['BqplotPathSlicerMode', 'BqplotPathSlicerCrosshairMode']


class _NoInteractMixin(InteractCheckableTool):
    """
    Like :class:`InteractCheckableTool` but doesn't wire ``self.interact``
    into the viewer's mouse interaction. Subclasses just consume events
    through ``add_event_callback``.
    """
    interact = None

    def activate(self):
        # Don't call super().activate() -- that would try to set
        # self.viewer._mouse_interact.next = self.interact which is None.
        pass

    def deactivate(self):
        pass


@viewer_tool
class BqplotPathSlicerMode(_NoInteractMixin):
    """
    Click to add path vertices, Enter to materialise a
    :class:`PathSlicedData` for each Data layer in the source viewer
    and open a PV viewer, Escape to clear the in-progress path.
    """

    icon = 'glue_slice'
    tool_id = 'bqplot:slice'
    action_text = 'Slice Extraction'
    tool_tip = ('Click to add path vertices, ENTER to extract a PV '
                'slice, ESC to clear the path.')
    status_tip = tool_tip

    def __init__(self, viewer, **kwargs):
        super().__init__(viewer, **kwargs)
        self._vx = []
        self._vy = []
        self._line = Lines(x=[], y=[],
                           scales={'x': self.viewer.scale_x,
                                   'y': self.viewer.scale_y},
                           colors=[INTERACT_COLOR], stroke_width=2,
                           marker='circle', marker_size=24)
        self._pv_viewer = None
        self._added_to_figure = False
        self.viewer.state.add_callback('reference_data',
                                       self._on_reference_data_change)
        self._on_reference_data_change()

    def _on_reference_data_change(self, *args):
        if self.viewer is None:
            return
        ref = self.viewer.state.reference_data
        if ref is not None:
            self.enabled = ref.ndim == 3

    def activate(self):
        if not self._added_to_figure:
            self.viewer.figure.marks = list(self.viewer.figure.marks) + [self._line]
            self._added_to_figure = True
        try:
            self.viewer.remove_event_callback(self._on_event)
        except KeyError:
            pass
        self.viewer.add_event_callback(self._on_event,
                                       events=['click', 'keydown'])

    def deactivate(self):
        try:
            self.viewer.remove_event_callback(self._on_event)
        except KeyError:
            pass

    def _on_event(self, event):
        name = event['event']
        if name == 'click':
            self._vx.append(event['domain']['x'])
            self._vy.append(event['domain']['y'])
            self._line.x = list(self._vx)
            self._line.y = list(self._vy)
        elif name == 'keydown':
            key = event.get('key', '')
            if key in ('Enter', 'Return') and len(self._vx) >= 2:
                self._finalize()
            elif key == 'Escape':
                self._clear_path()

    def _clear_path(self):
        self._vx = []
        self._vy = []
        self._line.x = []
        self._line.y = []

    def _finalize(self):
        vx = np.array(self._vx)
        vy = np.array(self._vy)
        self._extract(vx, vy)
        self._clear_path()

    def _extract(self, vx, vy):
        opened_viewer = self._pv_viewer is None
        if opened_viewer:
            self._pv_viewer = self.viewer.session.application.new_data_viewer(
                BqplotImageView)

        updated = build_or_update_pvs(self.viewer, vx, vy)

        if opened_viewer:
            for pv, layer_state in updated:
                self._pv_viewer.add_data(pv)
                pvstate = layer_state.as_dict()
                pvstate.pop('layer', None)
                for new_layer_state in self._pv_viewer.state.layers[::-1]:
                    if new_layer_state.layer is pv:
                        try:
                            new_layer_state.update_from_dict(pvstate)
                        except ValueError:
                            pass
                        break
            self._pv_viewer.state.aspect = 'auto'
            self._pv_viewer.state.reset_limits()


@viewer_tool
class BqplotPathSlicerCrosshairMode(_NoInteractMixin):
    """
    Tool for the PV viewer that, when mouse-moved, draws the path on
    the parent cube viewer, highlights the cursor's projection back to
    parent-pixel coordinates, and pushes the cursor's PV-y onto the
    parent viewer's ``state.slices`` (which is backend-agnostic).
    """

    icon = 'glue_path'
    tool_id = 'bqplot:pv_crosshair'
    action_text = 'Show position on original path'
    tool_tip = 'Move over the PV viewer to highlight the cursor on the parent.'
    status_tip = tool_tip

    def __init__(self, viewer, **kwargs):
        super().__init__(viewer, **kwargs)
        self._path_line = None
        self._crosshair = None
        self.viewer.state.add_callback('reference_data',
                                       self._on_reference_data_change)
        self._on_reference_data_change()

    def _on_reference_data_change(self, *args):
        if self.viewer is None:
            return
        from glue.plugins.tools.pv_slicer.path_sliced_data import PathSlicedData
        ref = self.viewer.state.reference_data
        self.enabled = isinstance(ref, PathSlicedData) \
            and getattr(ref, 'parent_viewer', None) is not None

    def activate(self):
        from glue.plugins.tools.pv_slicer.path_sliced_data import PathSlicedData
        ref = self.viewer.state.reference_data
        if not isinstance(ref, PathSlicedData):
            return
        parent = ref.parent_viewer
        self._path_line = Lines(x=list(ref.x), y=list(ref.y),
                                scales={'x': parent.scale_x,
                                        'y': parent.scale_y},
                                colors=['#669dff'], stroke_width=2)
        self._crosshair = Scatter(x=[], y=[],
                                  scales={'x': parent.scale_x,
                                          'y': parent.scale_y},
                                  marker='cross', colors=['#669dff'],
                                  default_size=144)
        parent.figure.marks = list(parent.figure.marks) + [
            self._path_line, self._crosshair]
        self.viewer.add_event_callback(self._on_move, events=['mousemove'])

    def deactivate(self):
        try:
            self.viewer.remove_event_callback(self._on_move)
        except KeyError:
            pass
        from glue.plugins.tools.pv_slicer.path_sliced_data import PathSlicedData
        ref = self.viewer.state.reference_data
        if isinstance(ref, PathSlicedData) and ref.parent_viewer is not None:
            parent = ref.parent_viewer
            parent.figure.marks = [m for m in parent.figure.marks
                                   if m is not self._path_line
                                   and m is not self._crosshair]
        self._path_line = None
        self._crosshair = None

    def _on_move(self, event):
        from glue.plugins.tools.pv_slicer.path_sliced_data import PathSlicedData
        ref = self.viewer.state.reference_data
        if not isinstance(ref, PathSlicedData):
            return
        xdata = event['domain']['x']
        ydata = event['domain']['y']
        ind = int(round(np.clip(xdata, 0, ref.shape[-1] - 1)))
        self._crosshair.x = [ref.x[ind]]
        self._crosshair.y = [ref.y[ind]]
        drive_parent_slice(ref, ydata)
