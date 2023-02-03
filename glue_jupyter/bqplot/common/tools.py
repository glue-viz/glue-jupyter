from contextlib import nullcontext

import os
from bqplot import PanZoom
from bqplot.interacts import BrushSelector, BrushIntervalSelector
from bqplot_image_gl.interacts import BrushEllipseSelector
from glue.core.roi import RectangularROI, RangeROI, CircularROI, EllipticalROI, PolygonalROI
from glue.core.subset import RoiSubsetState
from glue.config import viewer_tool
from glue.viewers.common.tool import Tool, CheckableTool
import numpy as np

__all__ = []

ICON_WIDTH = 20
INTERACT_COLOR = '#cbcbcb'

ICONS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'icons')


class InteractCheckableTool(CheckableTool):

    def __init__(self, viewer):
        self.viewer = viewer

    def activate(self):

        # Disable any active tool in other viewers
        if self.viewer.session.application.get_setting('single_global_active_tool'):
            for viewer in self.viewer.session.application.viewers:
                if viewer is not self.viewer:
                    viewer.toolbar.active_tool = None

        self.viewer._mouse_interact.next = self.interact

    def deactivate(self):
        self.viewer._mouse_interact.next = None


class BqplotSelectionTool(InteractCheckableTool):

    def activate(self):
        # Jumps back to "create new" if that setting is active
        if self.viewer.session.application.get_setting('new_subset_on_selection_tool_change'):
            self.viewer.session.edit_subset_mode.edit_subset = None
        super().activate()


@viewer_tool
class BqplotPanZoomMode(InteractCheckableTool):

    icon = 'glue_move'
    tool_id = 'bqplot:panzoom'
    action_text = 'Pan and Zoom'
    tool_tip = 'Interactively pan (click-drag) and zoom (scroll) around'

    def __init__(self, viewer, **kwargs):

        super().__init__(viewer, **kwargs)

        self.interact = PanZoom(scales={'x': [self.viewer.scale_x],
                                        'y': [self.viewer.scale_y]})

    def activate(self):
        if hasattr(self.viewer, '_composite_image'):
            self.viewer.state.add_callback('image_external_padding', self._sync_padding)
            self._sync_padding()
        super().activate()

    def _sync_padding(self, *args):
        self.viewer._composite_image.external_padding = self.viewer.state.image_external_padding

    def deactivate(self):
        if hasattr(self.viewer, '_composite_image'):
            self.viewer.state.remove_callback('image_external_padding', self._sync_padding)
            self.viewer._composite_image.external_padding = 0
        super().deactivate()


@viewer_tool
class BqplotPanZoomXMode(InteractCheckableTool):

    icon = 'glue_move_x'
    tool_id = 'bqplot:panzoom_x'
    action_text = 'Pan and Zoom X Axis'
    tool_tip = 'Interactively pan and zoom x axis only'

    def __init__(self, viewer, **kwargs):

        super().__init__(viewer, **kwargs)

        self.interact = PanZoom(scales={'x': [self.viewer.scale_x]})


@viewer_tool
class BqplotPanZoomYMode(InteractCheckableTool):

    icon = 'glue_move_y'
    tool_id = 'bqplot:panzoom_y'
    action_text = 'Pan and Zoom Y Axis'
    tool_tip = 'Interactively pan and zoom y axis only'

    def __init__(self, viewer, **kwargs):

        super().__init__(viewer, **kwargs)

        self.interact = PanZoom(scales={'y': [self.viewer.scale_y]})


@viewer_tool
class BqplotRectangleMode(BqplotSelectionTool):

    icon = 'glue_square'
    tool_id = 'bqplot:rectangle'
    action_text = 'Rectangular ROI'
    tool_tip = 'Define a rectangular region of interest'

    def __init__(self, viewer, roi=None, finalize_callback=None, **kwargs):

        super().__init__(viewer, **kwargs)

        self.interact = BrushSelector(x_scale=self.viewer.scale_x,
                                      y_scale=self.viewer.scale_y,
                                      color=INTERACT_COLOR)

        if roi is not None:
            self.update_from_roi(roi)

        self.interact.observe(self.update_selection, "brushing")
        self.interact.observe(self.on_selection_change, "selected_x")
        self.interact.observe(self.on_selection_change, "selected_y")
        self.finalize_callback = finalize_callback

    def update_selection(self, *args):
        if self.interact.brushing:
            return
        with self.viewer._output_widget or nullcontext():
            if self.interact.selected_x is not None and self.interact.selected_y is not None:
                x = self.interact.selected_x
                y = self.interact.selected_y
                roi = RectangularROI(xmin=min(x), xmax=max(x), ymin=min(y), ymax=max(y))
                self.viewer.apply_roi(roi)
                if self.finalize_callback is not None:
                    self.finalize_callback()

    def update_from_roi(self, roi):
        with self.viewer._output_widget or nullcontext():
            if isinstance(roi, RectangularROI):
                self.interact.selected_x = [roi.xmin, roi.xmax]
                self.interact.selected_y = [roi.ymin, roi.ymax]
            elif isinstance(roi, PolygonalROI):
                self.interact.selected_x = [np.min(roi.vx), np.max(roi.vx)]
                self.interact.selected_y = [np.min(roi.vy), np.max(roi.vy)]
            else:
                raise TypeError(f'Cannot initialize a BqplotRectangleMode from a {type(roi)}')
            # FIXME: the brush selector does not actually update unless the
            # widget is resized/refreshed, see
            # https://github.com/bloomberg/bqplot/issues/1067

    def on_selection_change(self, *args):
        if self.interact.selected_x is None or self.interact.selected_y is None:
            if self.finalize_callback is not None:
                self.finalize_callback()

    def activate(self):
        with self.viewer._output_widget or nullcontext():
            self.interact.selected_x = None
            self.interact.selected_y = None
        super().activate()


@viewer_tool
class BqplotCircleMode(BqplotSelectionTool):

    icon = 'glue_circle'
    tool_id = 'bqplot:circle'
    action_text = 'Circular ROI'
    tool_tip = 'Define a circular region of interest'

    def __init__(self, viewer, roi=None, finalize_callback=None, **kwargs):

        super().__init__(viewer, **kwargs)

        self.interact = BrushEllipseSelector(x_scale=self.viewer.scale_x,
                                             y_scale=self.viewer.scale_y,
                                             pixel_aspect=1)

        # Workaround for bug that causes the `color` trait to not be recognized
        style = self.interact.style.copy()
        style['fill'] = INTERACT_COLOR
        border_style = self.interact.border_style.copy()
        border_style['fill'] = INTERACT_COLOR
        border_style['stroke'] = INTERACT_COLOR
        self.interact.style = style
        self.interact.border_style = border_style

        if roi is not None:
            self.update_from_roi(roi)

        self.interact.observe(self.update_selection, "brushing")
        self.interact.observe(self.on_selection_change, "selected_x")
        self.interact.observe(self.on_selection_change, "selected_y")
        self.finalize_callback = finalize_callback

    def update_selection(self, *args):
        if self.interact.brushing:
            return
        with self.viewer._output_widget or nullcontext():
            if self.interact.selected_x is not None and self.interact.selected_y is not None:
                x = self.interact.selected_x
                y = self.interact.selected_y
                # similar to https://github.com/glue-viz/glue/blob/b14ccffac6a5
                # 271c2869ead9a562a2e66232e397/glue/core/roi.py#L1275-L1297
                # We should now check if the radius in data coordinates is the same
                # along x and y, as if so then we can return a circle, otherwise we
                # should return an ellipse.
                xc = x.mean()
                yc = y.mean()
                rx = abs(x[1] - x[0])/2
                ry = abs(y[1] - y[0])/2
                # We use a tolerance of 1e-2 below to match the tolerance set in glue-core
                # https://github.com/glue-viz/glue/blob/6b968b352bc5ad68b95ad5e3bb25550782a69ee8/glue/viewers/matplotlib/state.py#L198
                if np.allclose(rx, ry, rtol=1e-2):
                    roi = CircularROI(xc=xc, yc=yc, radius=rx)
                else:
                    roi = EllipticalROI(xc=xc, yc=yc, radius_x=rx, radius_y=ry)
                self.viewer.apply_roi(roi)
                if self.finalize_callback is not None:
                    self.finalize_callback()

    def update_from_roi(self, roi):
        if isinstance(roi, CircularROI):
            rx = ry = roi.radius
        elif isinstance(roi, EllipticalROI):
            rx, ry = roi.radius_x, roi.radius_y
        else:
            raise TypeError(f'Cannot initialize a BqplotCircleMode from a {type(roi)}')
        self.interact.selected_x = [roi.xc - rx, roi.xc + rx]
        self.interact.selected_y = [roi.yc - ry, roi.yc + ry]

    def on_selection_change(self, *args):
        if self.interact.selected_x is None or self.interact.selected_y is None:
            if self.finalize_callback is not None:
                self.finalize_callback()

    def activate(self):
        with self.viewer._output_widget or nullcontext():
            self.interact.selected_x = None
            self.interact.selected_y = None
        super().activate()


@viewer_tool
class BqplotEllipseMode(BqplotCircleMode):

    icon = os.path.join(ICONS_DIR, 'glue_ellipse.svg')
    tool_id = 'bqplot:ellipse'
    action_text = 'Elliptical ROI'
    tool_tip = 'Define an elliptical region of interest'

    def __init__(self, viewer, roi=None, finalize_callback=None, **kwargs):

        super().__init__(viewer, **kwargs)

        self.interact = BrushEllipseSelector(x_scale=self.viewer.scale_x,
                                             y_scale=self.viewer.scale_y)

        # Workaround for bug that causes the `color` trait to not be recognized
        style = self.interact.style.copy()
        style['fill'] = INTERACT_COLOR
        border_style = self.interact.border_style.copy()
        border_style['fill'] = INTERACT_COLOR
        border_style['stroke'] = INTERACT_COLOR
        self.interact.style = style
        self.interact.border_style = border_style

        if roi is not None:
            self.update_from_roi(roi)

        self.interact.observe(self.update_selection, "brushing")
        self.interact.observe(self.on_selection_change, "selected_x")
        self.interact.observe(self.on_selection_change, "selected_y")
        self.finalize_callback = finalize_callback


@viewer_tool
class BqplotXRangeMode(BqplotSelectionTool):

    icon = 'glue_xrange_select'
    tool_id = 'bqplot:xrange'
    action_text = 'X range ROI'
    tool_tip = 'Select a range of x values'

    def __init__(self, viewer, **kwargs):

        super().__init__(viewer, **kwargs)

        self.interact = BrushIntervalSelector(scale=self.viewer.scale_x,
                                              color=INTERACT_COLOR)

        self.interact.observe(self.update_selection, "brushing")

    def update_selection(self, *args):
        with self.viewer._output_widget or nullcontext():
            if self.interact.selected is not None:
                x = self.interact.selected
                if x is not None and len(x):
                    roi = RangeROI(min=min(x), max=max(x), orientation='x')
                    self.viewer.apply_roi(roi)

    def activate(self):
        with self.viewer._output_widget or nullcontext():
            self.interact.selected = None
        super().activate()


@viewer_tool
class BqplotYRangeMode(BqplotSelectionTool):

    icon = 'glue_yrange_select'
    tool_id = 'bqplot:yrange'
    action_text = 'Y range ROI'
    tool_tip = 'Select a range of y values'

    def __init__(self, viewer, **kwargs):

        super().__init__(viewer, **kwargs)

        self.interact = BrushIntervalSelector(scale=self.viewer.scale_y,
                                              orientation='vertical',
                                              color=INTERACT_COLOR)

        self.interact.observe(self.update_selection, "brushing")

    def update_selection(self, *args):
        with self.viewer._output_widget or nullcontext():
            if self.interact.selected is not None:
                y = self.interact.selected
                if y is not None and len(y):
                    roi = RangeROI(min=min(y), max=max(y), orientation='y')
                    self.viewer.apply_roi(roi)

    def activate(self):
        with self.viewer._output_widget or nullcontext():
            self.interact.selected = None
        super().activate()


# The following is deliberately not a viewer_tool, it is an 'invisible' mode
# that can be activated when other tools are inactive.


class ROIClickAndDrag(InteractCheckableTool):
    """
    A tool that enables clicking and dragging of existing ROIs.
    """

    def __init__(self, viewer, **kwargs):

        super().__init__(viewer, **kwargs)

        self.viewer = viewer
        self._edit_subset_mode = viewer.session.edit_subset_mode
        self.interact = None
        self._active_tool = None

    def activate(self):
        super().activate()
        self.viewer.add_event_callback(self.on_msg, events=['dragstart'])

    def deactivate(self):
        self.viewer.remove_event_callback(self.on_msg)
        super().deactivate()

    def on_msg(self, event):
        name = event['event']
        domain = event['domain']
        x, y = domain['x'], domain['y']
        if name == 'dragstart':
            self.press(x, y)

    def press(self, x, y):
        from glue_jupyter.bqplot.image.layer_artist import BqplotImageSubsetLayerArtist
        for layer in self.viewer.layers:
            if not isinstance(layer, BqplotImageSubsetLayerArtist):
                continue
            subset_state = layer.state.layer.subset_state
            if layer.visible and isinstance(subset_state, RoiSubsetState):
                roi = subset_state.roi
                if roi.contains(x, y):
                    if isinstance(roi, (EllipticalROI, CircularROI)):
                        self._active_tool = BqplotCircleMode(self.viewer, roi=roi,
                                                             finalize_callback=self.release)
                        self.viewer._mouse_interact.next = self._active_tool.interact
                    elif isinstance(roi, (PolygonalROI, RectangularROI)):
                        self._active_tool = BqplotRectangleMode(self.viewer, roi=roi,
                                                                finalize_callback=self.release)
                        self.viewer._mouse_interact.next = self._active_tool.interact
                    else:
                        raise TypeError(f"Unexpected ROI type: {type(roi)}")
                    self._edit_subset_mode.edit_subset = [layer.state.layer.group]
                    break
        else:
            self._selected = False

    def release(self):
        self.viewer._mouse_interact.next = None


@viewer_tool
class HomeTool(Tool):

    tool_id = 'bqplot:home'
    icon = 'glue_home'
    action_text = 'Home'
    tool_tip = 'Reset original zoom'

    def activate(self):
        self.viewer.state.reset_limits()
