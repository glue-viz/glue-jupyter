"""
PV slicer tool for the matplotlib Jupyter image viewer.

Subclasses glue-core's :class:`~glue.viewers.matplotlib.toolbar_mode.PathMode`
(which already handles click-to-add-vertex / Enter-to-finalise) and on
finalise materialises PathSlicedData instances for every Data layer in
the source viewer, opens an :class:`ImageJupyterViewer` to display them,
and wires the link graph.
"""
import numpy as np
from matplotlib.lines import Line2D

from glue.config import viewer_tool
from glue.viewers.matplotlib.toolbar_mode import PathMode, ToolbarModeBase
from glue.plugins.tools.pv_slicer.path_sliced_data import PathSlicedData

from glue_jupyter.matplotlib.image import ImageJupyterViewer

from .common import build_or_update_pvs, drive_parent_slice


__all__ = ['MatplotlibJupyterPathSlicerMode',
           'MatplotlibJupyterPathSlicerCrosshairMode']


@viewer_tool
class MatplotlibJupyterPathSlicerMode(PathMode):

    icon = 'glue_slice'
    tool_id = 'jupyter:slice'
    action_text = 'Slice Extraction'
    tool_tip = ('Extract a slice from an arbitrary path\n'
                '  ENTER accepts the path\n'
                '  ESCAPE clears the path')
    status_tip = ('Draw a path then press ENTER to extract slice, '
                  'or press ESC to cancel')
    shortcut = 'P'

    def __init__(self, viewer, **kwargs):
        super().__init__(viewer, **kwargs)
        self._roi_callback = self._extract_callback
        self._pv_viewer = None
        self.viewer.state.add_callback('reference_data',
                                       self._on_reference_data_change)
        self._on_reference_data_change()

    def _on_reference_data_change(self, *args):
        ref = self.viewer.state.reference_data
        if ref is not None:
            self.enabled = ref.ndim == 3

    def _extract_callback(self, mode):
        vx, vy = mode.roi().to_polygon()
        self._open_or_update(vx, vy)

    def _open_or_update(self, vx, vy):
        opened_viewer = self._pv_viewer is None
        if opened_viewer:
            self._pv_viewer = self.viewer.session.application.new_data_viewer(
                ImageJupyterViewer)

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
            self._pv_viewer.state.color_mode = self.viewer.state.color_mode
            self._pv_viewer.state.reset_limits()


@viewer_tool
class MatplotlibJupyterPathSlicerCrosshairMode(ToolbarModeBase):

    icon = 'glue_path'
    tool_id = 'jupyter:pv_crosshair'
    action_text = 'Show position on original path'
    tool_tip = 'Click and drag to show position of cursor on original slice.'
    status_tip = tool_tip

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._move_callback = self._on_move
        self._press_callback = self._on_press
        self._release_callback = self._on_release
        self._active = False
        self._line = None
        self._crosshair = None
        self.data = None
        self.viewer.state.add_callback('reference_data',
                                       self._on_reference_data_change)
        self._on_reference_data_change()

    def _on_reference_data_change(self, *args):
        ref = self.viewer.state.reference_data
        self.enabled = isinstance(ref, PathSlicedData) \
            and getattr(ref, 'parent_viewer', None) is not None
        self.data = ref if self.enabled else None

    def activate(self):
        self._line = Line2D(self.data.x, self.data.y, zorder=1000,
                            color='#669dff', alpha=0.6, lw=2)
        self.data.parent_viewer.axes.add_line(self._line)
        self._crosshair = self.data.parent_viewer.axes.plot(
            [], [], '+', ms=12, mfc='none', mec='#669dff', mew=1,
            zorder=100)[0]
        self.data.parent_viewer.figure.canvas.draw_idle()
        super().activate()

    def deactivate(self):
        if self._line is not None:
            self._line.remove()
            self._line = None
        if self._crosshair is not None:
            self._crosshair.remove()
            self._crosshair = None
        if self.data is not None:
            self.data.parent_viewer.figure.canvas.draw_idle()
        super().deactivate()

    def _on_press(self, mode):
        self._active = True

    def _on_release(self, mode):
        self._active = False

    def _on_move(self, mode):
        if not self._active or self.data is None:
            return
        xdata, ydata = self._event_xdata, self._event_ydata
        if xdata is None or ydata is None:
            return
        ind = int(round(np.clip(xdata, 0, self.data.shape[-1] - 1)))
        x = self.data.x[ind]
        y = self.data.y[ind]
        self._crosshair.set_xdata([x])
        self._crosshair.set_ydata([y])
        drive_parent_slice(self.data, ydata)
        self.data.parent_viewer.figure.canvas.draw_idle()
