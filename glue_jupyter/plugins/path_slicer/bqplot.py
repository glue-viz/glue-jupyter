"""
Path slicer tool for the bqplot image viewer.

bqplot has no analogue of matplotlib's :class:`PathMode`, so this
module implements a small click-to-add-vertex / Enter-to-finalise
tool on top of the viewer's ``add_event_callback`` machinery. The
multi-trace data model parallels glue-core's
:class:`BasePathSlicerMode`: each Enter produces one
:class:`PathSlicedData` per cube layer and opens a fresh slice
viewer, or refreshes an existing trace if one has been selected as
the next-Enter target via the toolbar's chevron menu (see
:mod:`glue_jupyter.common.toolbar_vuetify`). Overlays on the source
viewer are bqplot ``Lines`` rather than matplotlib ``Line2D``.
"""
import numpy as np

from bqplot import Lines, Scatter

from glue.config import viewer_tool
from glue.plugins.tools.path_slicer.common import drive_parent_slice
from glue.plugins.tools.path_slicer.multi_trace import (
    MultiTracePathSlicerMixin)
from glue.plugins.tools.path_slicer.path_sliced_data import PathSlicedData

from glue_jupyter.bqplot.common.tools import (InteractCheckableTool,
                                              INTERACT_COLOR)
from glue_jupyter.bqplot.image import BqplotImageView


__all__ = ['BqplotPathSlicerMode', 'BqplotPathSlicerCrosshairMode']


_PATH_COLOR = '#669dff'
_PATH_OPACITY_ACTIVE = 1.0
_PATH_OPACITY_INACTIVE = 0.3


class _NoInteractMixin(InteractCheckableTool):
    """
    Like :class:`InteractCheckableTool` but with no bqplot ``Interact``
    of its own. Subclasses consume events through
    :func:`add_event_callback` and fully override ``activate`` /
    ``deactivate`` (no ``super()`` chaining), which is why setting
    :attr:`interact` to ``None`` is safe -- the inherited
    ``InteractCheckableTool.activate`` is never reached.
    """
    interact = None


@viewer_tool
class BqplotPathSlicerMode(MultiTracePathSlicerMixin, _NoInteractMixin):
    """
    Click to add path vertices, Enter to materialise a trace
    (one :class:`PathSlicedData` per Data layer in the source viewer)
    and open a fresh slice viewer; Escape clears the in-progress path.

    The "Create new / Update path N" target picker is the chevron
    dropdown attached to this tool's toolbar button (see
    :class:`glue_jupyter.common.toolbar_vuetify.BasicJupyterToolbar`).
    """

    icon = 'glue_slice'
    tool_id = 'bqplot:slice'
    action_text = 'Slice Extraction'
    tool_tip = ('Click to add path vertices, ENTER to extract a path '
                'slice, ESC to clear the path.')
    status_tip = tool_tip

    slice_viewer_cls = BqplotImageView

    def __init__(self, viewer, **kwargs):
        super().__init__(viewer, **kwargs)
        # In-progress path being drawn (cleared after Enter / Escape).
        self._vx = []
        self._vy = []
        self._line = Lines(x=[], y=[],
                           scales={'x': self.viewer.scale_x,
                                   'y': self.viewer.scale_y},
                           colors=[INTERACT_COLOR], stroke_width=2,
                           marker='circle', marker_size=24)
        self._added_to_figure = False

        self._init_multi_trace()
        # bqplot Lines mark per trace, drawn on the source viewer.
        self._overlays = {}

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
        self._open_or_update(vx, vy)
        self._clear_path()

    # ------------------------------------------------------------------
    # bqplot overlay drawing (mixin hooks)
    # ------------------------------------------------------------------

    def _refresh_overlays(self):
        current_keys = {id(trace) for trace in self._traces}
        # Drop overlays for traces that no longer exist.
        stale = [k for k in self._overlays if k not in current_keys]
        if stale:
            kept = [m for m in self.viewer.figure.marks
                    if all(self._overlays.get(k) is not m for k in stale)]
            self.viewer.figure.marks = kept
            for k in stale:
                self._overlays.pop(k, None)

        for trace in self._traces:
            key = id(trace)
            x = list(trace[0].x)
            y = list(trace[0].y)
            opacity = (_PATH_OPACITY_ACTIVE if trace is self._target_trace
                       else _PATH_OPACITY_INACTIVE)
            if key in self._overlays:
                line = self._overlays[key]
                line.x = x
                line.y = y
                line.opacities = [opacity]
            else:
                line = Lines(x=x, y=y,
                             scales={'x': self.viewer.scale_x,
                                     'y': self.viewer.scale_y},
                             colors=[_PATH_COLOR], stroke_width=2,
                             opacities=[opacity])
                self.viewer.figure.marks = list(self.viewer.figure.marks) + [line]
                self._overlays[key] = line


@viewer_tool
class BqplotPathSlicerCrosshairMode(_NoInteractMixin):
    """
    Tool for the slice viewer that, when mouse-moved, draws the path on
    the parent cube viewer, highlights the cursor's projection back to
    parent-pixel coordinates, and pushes the cursor's slice y onto the
    parent viewer's ``state.slices`` (which is backend-agnostic).
    """

    icon = 'glue_path'
    tool_id = 'bqplot:path_crosshair'
    action_text = 'Show position on original path'
    tool_tip = 'Move over the slice viewer to highlight the cursor on the parent.'
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
        ref = self.viewer.state.reference_data
        self.enabled = isinstance(ref, PathSlicedData) \
            and getattr(ref, 'parent_viewer', None) is not None

    def activate(self):
        ref = self.viewer.state.reference_data
        if not isinstance(ref, PathSlicedData):
            return
        parent = ref.parent_viewer
        self._path_line = Lines(x=list(ref.x), y=list(ref.y),
                                scales={'x': parent.scale_x,
                                        'y': parent.scale_y},
                                colors=[_PATH_COLOR], stroke_width=2)
        self._crosshair = Scatter(x=[], y=[],
                                  scales={'x': parent.scale_x,
                                          'y': parent.scale_y},
                                  marker='cross', colors=[_PATH_COLOR],
                                  default_size=144)
        parent.figure.marks = list(parent.figure.marks) + [
            self._path_line, self._crosshair]
        self.viewer.add_event_callback(self._on_move, events=['mousemove'])

    def deactivate(self):
        try:
            self.viewer.remove_event_callback(self._on_move)
        except KeyError:
            pass
        ref = self.viewer.state.reference_data
        if isinstance(ref, PathSlicedData) and ref.parent_viewer is not None:
            parent = ref.parent_viewer
            parent.figure.marks = [m for m in parent.figure.marks
                                   if m is not self._path_line
                                   and m is not self._crosshair]
        self._path_line = None
        self._crosshair = None

    def _on_move(self, event):
        ref = self.viewer.state.reference_data
        if not isinstance(ref, PathSlicedData):
            return
        xdata = event['domain']['x']
        ydata = event['domain']['y']
        ind = round(np.clip(xdata, 0, ref.shape[-1] - 1))
        self._crosshair.x = [ref.x[ind]]
        self._crosshair.y = [ref.y[ind]]
        drive_parent_slice(ref, ydata)
