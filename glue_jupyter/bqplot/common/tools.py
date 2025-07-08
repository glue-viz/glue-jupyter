import os
from contextlib import nullcontext

import numpy as np
from bqplot import PanZoom, Lines
from bqplot.interacts import BrushSelector, BrushIntervalSelector
from bqplot_image_gl.interacts import BrushEllipseSelector
from glue import __version__ as glue_version
from glue.core.roi import RectangularROI, RangeROI, CircularROI, EllipticalROI, PolygonalROI
from glue.core.subset import RoiSubsetState
from glue.config import viewer_tool
from glue.viewers.common.tool import Tool, CheckableTool
from packaging.version import Version

GLUE_LT_1_11 = Version(glue_version) < Version("1.11")

if not GLUE_LT_1_11:
    from glue.core.roi import CircularAnnulusROI
else:
    CircularAnnulusROI = None

__all__ = []

ICON_WIDTH = 20
INTERACT_COLOR = '#cbcbcb'

ICONS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'icons')


class TrueCircularROI(CircularROI):
    pass


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
        if hasattr(self, '_roi'):
            self._roi = None


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

        self._roi = kwargs.get("roi", None)
        if roi is not None:
            self.update_from_roi(roi)

        self.interact.observe(self.update_selection, "brushing")
        self.interact.observe(self.on_selection_change, "selected")
        self.finalize_callback = finalize_callback

    def update_selection(self, *args):
        if self.interact.brushing:
            return
        with self.viewer._output_widget or nullcontext():
            if self.interact.selected_x is not None and self.interact.selected_y is not None:
                x = self.interact.selected_x
                y = self.interact.selected_y
                theta = None if self._roi is None else self._roi.theta
                roi = RectangularROI(xmin=min(x), xmax=max(x), ymin=min(y), ymax=max(y), theta=theta)  # noqa: E501
                self._roi = roi
                self.viewer.apply_roi(roi)
                if self.finalize_callback is not None:
                    self.finalize_callback()

    def update_from_roi(self, roi):
        self._roi = roi
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
class BqplotPolygonMode(BqplotSelectionTool):
    """
    Since Bqplot LassoSelector does not allow us to get the coordinates of the
    selection (see https://github.com/bqplot/bqplot/pull/674), we simply use
    a callback on the default viewer MouseInteraction and a patch to display
    the selection. The parent class defaults to setting polygon vertices by
    clicking in the selector.
    The polygon is closed by clicking within 2 % distance (of maximum extent)
    of the initial vertex, or on deactivating the tool.
    """
    icon = os.path.join(ICONS_DIR, 'glue_polygon')
    tool_id = 'bqplot:polygon'
    action_text = 'Polygonal ROI'
    tool_tip = 'Define a polygonal region of interest'

    def __init__(self, viewer, roi=None, finalize_callback=None, **kwargs):

        super().__init__(viewer, **kwargs)

        self.patch = Lines(x=[[]], y=[[]], fill_colors=[INTERACT_COLOR], colors=[INTERACT_COLOR],
                           opacities=[0.6], fill='inside', close_path=True,
                           scales={'x': self.viewer.scale_x, 'y': self.viewer.scale_y})

        self.interact = BrushSelector(x_scale=self.viewer.scale_x,
                                      y_scale=self.viewer.scale_y,
                                      color=INTERACT_COLOR)

        if roi is not None:
            self.update_from_roi(roi)

        self._lasso = False
        self.interact.observe(self.update_selection, "brushing")
        self.interact.observe(self.on_selection_change, "selected")
        self.finalize_callback = finalize_callback

    def update_selection(self, *args):
        if self.interact.brushing:
            return
        with self.viewer._output_widget or nullcontext():
            if self.interact.selected_x is not None and self.interact.selected_y is not None:
                x = self.interact.selected_x
                y = self.interact.selected_y
                dx = x.mean() - self._roi.centroid()[0]
                dy = y.mean() - self._roi.centroid()[1]

                roi = PolygonalROI(vx=np.array(self._roi.vx) + dx, vy=np.array(self._roi.vy) + dy)

                self._roi = roi
                self.viewer.apply_roi(roi)
                if self.finalize_callback is not None:
                    self.finalize_callback()

    def update_from_roi(self, roi):
        """
        Dragging with the `BrushSelector` using this method is still somewhat
        unintuitive, as the ROI position is not updated live; rather the target
        (centroid) position has to be set using the bounding bax shape.
        The method could potentially be extended to Circular and Rectangular
        ROIs using their `to_polygon` methods.
        """
        with self.viewer._output_widget or nullcontext():
            if isinstance(roi, PolygonalROI):
                self.patch.x = roi.vx
                self.patch.y = roi.vy
                self._roi = roi
            else:
                raise TypeError(f'Cannot initialize a BqplotPolygonMode from a {type(roi)}')

    def activate(self):
        """
        We do not call super().activate() because we don't have a separate interact,
        instead we just add a callback to the default viewer MouseInteraction.
        """

        # We need to make sure any existing callbacks associated with this
        # viewer are cleared. This can happen if the user switches between
        # different viewers without deactivating the tool.
        try:
            self.viewer.remove_event_callback(self.on_msg)
        except KeyError:
            pass

        # Disable any active tool in other viewers
        if self.viewer.session.application.get_setting('single_global_active_tool'):
            for viewer in self.viewer.session.application.viewers:
                if viewer is not self.viewer:
                    viewer.toolbar.active_tool = None
        self.viewer.add_event_callback(self.on_msg, events=['dragstart', 'dragmove', 'dragend'])

    def deactivate(self):
        if len(self.patch.x) > 1:
            self.close_vertices()
        try:
            self.viewer.remove_event_callback(self.on_msg)
        except KeyError:
            pass
        super().deactivate()

    def on_selection_change(self, *args):
        if self.interact.selected_x is None or self.interact.selected_y is None:
            if self.finalize_callback is not None:
                self.finalize_callback()

    def on_msg(self, event):
        name = event['event']
        domain = event['domain']
        x, y = domain['x'], domain['y']
        if name == 'dragstart' and len(self.patch.x) < 1:
            self.original_marks = list(self.viewer.figure.marks)
            self.viewer.figure.marks = self.original_marks + [self.patch]
            self.patch.x = [x]
            self.patch.y = [y]
        elif name == 'dragmove' and self._lasso:
            self.patch.x = np.append(self.patch.x, x)
            self.patch.y = np.append(self.patch.y, y)
        elif name == 'dragend':
            # If new point is within 2% of maximum extent of the origin, finalise the polygon.
            sz = max(self.patch.x) - min(self.patch.x), max(self.patch.y) - min(self.patch.y)
            if self._lasso or (abs(x - self.patch.x[0]) < 0.02 * sz[0] and
                               abs(y - self.patch.y[0]) < 0.02 * sz[1]):
                self.close_vertices()
            else:
                self.patch.x = np.append(self.patch.x, x)
                self.patch.y = np.append(self.patch.y, y)

    def close_vertices(self):
        roi = PolygonalROI(vx=self.patch.x, vy=self.patch.y)
        self.viewer.apply_roi(roi)

        new_marks = []
        for mark in self.viewer.figure.marks:
            if mark == self.patch:
                pass
            else:
                new_marks.append(mark)
        self.viewer.figure.marks = new_marks
        self.patch.x = [[]]
        self.patch.y = [[]]
        if self.finalize_callback is not None:
            self.finalize_callback()


@viewer_tool
class BqplotLassoMode(BqplotPolygonMode):
    """
    Subclass that defaults to creating a continous (lasso) polygonal selection
    by dragging the pointer along the outline.
    """

    icon = 'glue_lasso'
    tool_id = 'bqplot:lasso'
    tool_tip = 'Lasso a region of interest'

    def __init__(self, viewer, roi=None, finalize_callback=None, **kwargs):

        super().__init__(viewer, **kwargs)
        self._lasso = True


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
        self._strict_circle = False

        self._roi = kwargs.get("roi", None)
        if roi is not None:
            self.update_from_roi(roi)

        self.interact.observe(self.update_selection, "brushing")
        self.interact.observe(self.on_selection_change, "selected")
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
                # If _strict_circle set, enforce returning a circle; otherwise check
                # if the radius in data coordinates is (nearly) the same along x and y,
                # to return a circle as well, else we should return an ellipse.
                xc = x.mean()
                yc = y.mean()
                rx = abs(x[1] - x[0])/2
                ry = abs(y[1] - y[0])/2
                # We use a tolerance of 1e-2 below to match the tolerance set in glue-core
                # https://github.com/glue-viz/glue/blob/6b968b352bc5ad68b95ad5e3bb25550782a69ee8/glue/viewers/matplotlib/state.py#L198
                if self._strict_circle:
                    roi = TrueCircularROI(xc=xc, yc=yc, radius=np.sqrt((rx**2 + ry**2) * 0.5))
                elif np.allclose(rx, ry, rtol=1e-2):
                    roi = CircularROI(xc=xc, yc=yc, radius=(rx + ry) * 0.5)
                else:
                    theta = 0 if (self._roi is None or not hasattr(self._roi, "theta")) else self._roi.theta  # noqa: E501
                    roi = EllipticalROI(xc=xc, yc=yc, radius_x=rx, radius_y=ry, theta=theta)
                self._roi = roi
                self.viewer.apply_roi(roi)
                if self.finalize_callback is not None:
                    self.finalize_callback()

    def update_from_roi(self, roi):
        self._roi = roi
        if isinstance(roi, CircularROI):
            rx = ry = roi.radius
            if isinstance(roi, TrueCircularROI):
                self._strict_circle = True
        elif isinstance(roi, EllipticalROI):
            if self._strict_circle:
                rx, ry = np.sqrt((roi.radius_x ** 2 + roi.radius_y ** 2) * 0.5)
            else:
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
class BqplotTrueCircleMode(BqplotCircleMode):

    tool_id = 'bqplot:truecircle'
    tool_tip = 'Define a strictly circular region of interest'

    def __init__(self, viewer, roi=None, finalize_callback=None, **kwargs):

        super().__init__(viewer, **kwargs)
        self._strict_circle = True


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

        self._roi = kwargs.get("roi", None)
        if roi is not None:
            self.update_from_roi(roi)

        self.interact.observe(self.update_selection, "brushing")
        self.interact.observe(self.on_selection_change, "selected")
        self.finalize_callback = finalize_callback


@viewer_tool
class BqplotCircularAnnulusMode(BqplotCircleMode):

    icon = os.path.join(ICONS_DIR, 'glue_annulus.svg')
    tool_id = 'bqplot:circannulus'
    action_text = 'Circular Annulus ROI'
    tool_tip = 'Define a circular annulus region of interest'

    def __init__(self, *args, **kwargs):
        if GLUE_LT_1_11:
            raise NotImplementedError("This tool requires glue-core>=1.11")

        super().__init__(*args, **kwargs)
        self._roi = kwargs.get("roi", None)

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
                # make assumption to keep it circular.
                # Need extra float casting because of strict type check in CircularAnnulusROI.
                xc = float(x.mean())
                yc = float(y.mean())
                rx = abs(x[1] - x[0]) * 0.5
                ry = abs(y[1] - y[0]) * 0.5
                outer_r = float(rx + ry) * 0.5
                if self._roi is None:
                    inner_r = outer_r * 0.5  # Hardcoded for now, user can edit later.
                else:
                    # Resizing only changes outer r, avoid having inner_r >= outer_r afterwards.
                    inner_r = min(self._roi.inner_radius, outer_r * 0.999999)

                roi = CircularAnnulusROI(xc=xc, yc=yc, inner_radius=inner_r, outer_radius=outer_r)

                self._roi = roi
                self.viewer.apply_roi(roi)
                if self.finalize_callback is not None:
                    self.finalize_callback()

    def update_from_roi(self, roi):
        self._roi = roi
        if isinstance(roi, CircularAnnulusROI):
            rx = ry = roi.outer_radius
        else:
            raise TypeError(f'Cannot initialize a BqplotCircularAnnulusMode from a {type(roi)}')
        self.interact.selected_x = [roi.xc - rx, roi.xc + rx]
        self.interact.selected_y = [roi.yc - ry, roi.yc + ry]


@viewer_tool
class BqplotXRangeMode(BqplotSelectionTool):

    icon = 'glue_xrange_select'
    tool_id = 'bqplot:xrange'
    action_text = 'X range ROI'
    tool_tip = 'Select a range of x values'

    def __init__(self, viewer, roi=None, finalize_callback=None, **kwargs):

        super().__init__(viewer, **kwargs)

        self.interact = BrushIntervalSelector(scale=self.viewer.scale_x,
                                              color=INTERACT_COLOR)

        if roi is not None:
            self.update_from_roi(roi)

        self.interact.observe(self.update_selection, "brushing")
        self.interact.observe(self.on_selection_change, "selected")
        self.finalize_callback = finalize_callback

    def update_selection(self, *args):
        if self.interact.brushing:
            return
        with self.viewer._output_widget or nullcontext():
            if self.interact.selected is not None:
                x = self.interact.selected
                if x is not None and len(x):
                    roi = RangeROI(min=min(x), max=max(x), orientation='x')
                    self.viewer.apply_roi(roi)
                    if self.finalize_callback is not None:
                        self.finalize_callback()

    def update_from_roi(self, roi):
        with self.viewer._output_widget or nullcontext():
            if isinstance(roi, RangeROI):
                self.interact.selected = [roi.min, roi.max]
            else:
                raise TypeError(f'Cannot initialize a BqplotXRangeMode from a {type(roi)}')

    def on_selection_change(self, *args):
        if self.interact.selected is None:
            if self.finalize_callback is not None:
                self.finalize_callback()

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

    def __init__(self, viewer, roi=None, finalize_callback=None, **kwargs):

        super().__init__(viewer, **kwargs)

        self.interact = BrushIntervalSelector(scale=self.viewer.scale_y,
                                              orientation='vertical',
                                              color=INTERACT_COLOR)

        if roi is not None:
            self.update_from_roi(roi)

        self.interact.observe(self.update_selection, "brushing")
        self.interact.observe(self.on_selection_change, "selected")
        self.finalize_callback = finalize_callback

    def update_selection(self, *args):
        if self.interact.brushing:
            return
        with self.viewer._output_widget or nullcontext():
            if self.interact.selected is not None:
                y = self.interact.selected
                if y is not None and len(y):
                    roi = RangeROI(min=min(y), max=max(y), orientation='y')
                    self.viewer.apply_roi(roi)
                    if self.finalize_callback is not None:
                        self.finalize_callback()

    def update_from_roi(self, roi):
        with self.viewer._output_widget or nullcontext():
            if isinstance(roi, RangeROI):
                self.interact.selected = [roi.min, roi.max]
            else:
                raise TypeError(f'Cannot initialize a BqplotYRangeMode from a {type(roi)}')

    def on_selection_change(self, *args):
        if self.interact.selected is None:
            if self.finalize_callback is not None:
                self.finalize_callback()

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
                if roi.defined() and roi.contains(x, y):
                    if isinstance(roi, EllipticalROI):
                        self._active_tool = BqplotEllipseMode(
                            self.viewer, roi=roi, finalize_callback=self.release)
                    elif isinstance(roi, CircularROI):
                        self._active_tool = BqplotCircleMode(
                            self.viewer, roi=roi, finalize_callback=self.release)
                    elif isinstance(roi, RectangularROI):
                        self._active_tool = BqplotRectangleMode(
                            self.viewer, roi=roi, finalize_callback=self.release)
                    elif isinstance(roi, PolygonalROI):
                        self._active_tool = BqplotPolygonMode(
                            self.viewer, roi=roi, finalize_callback=self.release)
                    elif not GLUE_LT_1_11 and isinstance(roi, CircularAnnulusROI):
                        self._active_tool = BqplotCircularAnnulusMode(
                            self.viewer, roi=roi, finalize_callback=self.release)
                    else:
                        raise TypeError(f"Unexpected ROI type: {type(roi)}")
                    self.viewer._mouse_interact.next = self._active_tool.interact
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
