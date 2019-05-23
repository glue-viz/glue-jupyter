from bqplot import PanZoom
from bqplot.interacts import BrushSelector, BrushIntervalSelector
from glue.core.roi import RectangularROI, RangeROI
from glue.config import viewer_tool
from glue.viewers.common.tool import CheckableTool

__all__ = []

ICON_WIDTH = 20


class InteractCheckableTool(CheckableTool):

    def __init__(self, viewer):
        self.viewer = viewer

    def activate(self):
        self.viewer.figure.interaction = self.interact

    def deactivate(self):
        self.viewer.figure.interaction = None


@viewer_tool
class BqplotPanZoomMode(InteractCheckableTool):

    icon = 'glue_move'
    tool_id = 'bqplot:panzoom'
    action_text = 'Pan and Zoom'
    tool_tip = 'Interactively pan and zoom around'

    def __init__(self, viewer, **kwargs):

        super().__init__(viewer, **kwargs)

        self.interact = PanZoom(scales={'x': [self.viewer.scale_x],
                                        'y': [self.viewer.scale_y]})


@viewer_tool
class BqplotRectangleMode(InteractCheckableTool):

    icon = 'glue_square'
    tool_id = 'bqplot:rectangle'
    action_text = 'Rectangular ROI'
    tool_tip = 'Define a rectangular region of interest'

    def __init__(self, viewer, **kwargs):

        super().__init__(viewer, **kwargs)

        self.interact = BrushSelector(x_scale=self.viewer.scale_x,
                                      y_scale=self.viewer.scale_y,
                                      color="green")

        self.interact.observe(self.update_selection, "brushing")

    def update_selection(self, *args):
        with self.viewer._output_widget:
            if self.interact.selected_x is not None and self.interact.selected_y is not None:
                x = self.interact.selected_x
                y = self.interact.selected_y
                roi = RectangularROI(xmin=min(x), xmax=max(x), ymin=min(y), ymax=max(y))
                self.viewer.apply_roi(roi)


@viewer_tool
class BqplotXRangeMode(InteractCheckableTool):

    icon = 'glue_xrange_select'
    tool_id = 'bqplot:xrange'
    action_text = 'X range ROI'
    tool_tip = 'Select a range of x values'

    def __init__(self, viewer, **kwargs):

        super().__init__(viewer, **kwargs)

        self.interact = BrushIntervalSelector(scale=self.viewer.scale_x,
                                              color="green")

        self.interact.observe(self.update_selection, "brushing")

    def update_selection(self, *args):
        with self.viewer._output_widget:
            if self.interact.selected is not None:
                x = self.interact.selected
                if x is not None and len(x):
                    roi = RangeROI(min=min(x), max=max(x), orientation='x')
                    self.viewer.apply_roi(roi)


@viewer_tool
class BqplotYRangeMode(InteractCheckableTool):

    icon = 'glue_yrange_select'
    tool_id = 'bqplot:yrange'
    action_text = 'Y range ROI'
    tool_tip = 'Select a range of y values'

    def __init__(self, viewer, **kwargs):

        super().__init__(viewer, **kwargs)

        self.interact = BrushIntervalSelector(scale=self.viewer.scale_y,
                                              orientation='vertical',
                                              color="green")

        self.interact.observe(self.update_selection, "brushing")

    def update_selection(self, *args):
        with self.viewer._output_widget:
            if self.interact.selected is not None:
                y = self.interact.selected
                if y is not None and len(y):
                    roi = RangeROI(min=min(y), max=max(y), orientation='y')
                    self.viewer.apply_roi(roi)
