from contextlib import nullcontext

import numpy as np

from glue.core.roi import PolygonalROI, CircularROI, RectangularROI, Projected3dROI

from glue.config import viewer_tool
from glue.viewers.common.tool import CheckableTool

__all__ = []


class IPyVolumeCheckableTool(CheckableTool):

    def __init__(self, viewer):
        self.viewer = viewer
        self.viewer.figure.on_selection(self.on_selection)

    def activate(self):
        self.viewer.figure.selector = self.selector

    def deactivate(self):
        self.viewer.figure.selector = ''

    @property
    def projection_matrix(self):
        W = np.array(self.viewer.figure.matrix_world).reshape((4, 4))     .T  # noqa: N806
        P = np.array(self.viewer.figure.matrix_projection).reshape((4, 4)).T  # noqa: N806
        M = np.dot(P, W)  # noqa: N806
        return M


@viewer_tool
class IpyvolumeLassoMode(IPyVolumeCheckableTool):

    icon = 'glue_lasso'
    tool_id = 'ipyvolume:lasso'
    action_text = 'Polygon ROI'
    tool_tip = 'Define a polygonal region of interest'

    selector = 'lasso'

    def on_selection(self, data, other=None):

        if data['type'] != self.selector:
            return

        if data['device']:
            with self.viewer._output_widget or nullcontext():
                region = data['device']
                vx, vy = zip(*region)
                roi_2d = PolygonalROI(vx=vx, vy=vy)
                roi = Projected3dROI(roi_2d, self.projection_matrix)
                self.viewer.apply_roi(roi)


@viewer_tool
class IpyvolumeCircleMode(IPyVolumeCheckableTool):

    icon = 'glue_circle'
    tool_id = 'ipyvolume:circle'
    action_text = 'Circular ROI'
    tool_tip = 'Define a circular region of interest'

    selector = 'circle'

    def on_selection(self, data, other=None):

        if data['type'] != self.selector:
            return

        if data['device']:
            with self.viewer._output_widget or nullcontext():
                x1, y1 = data['device']['begin']
                x2, y2 = data['device']['end']
                dx = x2 - x1
                dy = y2 - y1
                r = (dx**2 + dy**2)**0.5
                roi_2d = CircularROI(xc=x1, yc=y1, radius=r)
                roi = Projected3dROI(roi_2d, self.projection_matrix)
                self.viewer.apply_roi(roi)


@viewer_tool
class IpyvolumeRectanglewMode(IPyVolumeCheckableTool):

    icon = 'glue_square'
    tool_id = 'ipyvolume:rectangle'
    action_text = 'Rectangular ROI'
    tool_tip = 'Define a rectangular region of interest'

    selector = 'rectangle'

    def on_selection(self, data, other=None):

        if data['type'] != self.selector:
            return

        if data['device']:
            with self.viewer._output_widget or nullcontext():
                x1, y1 = data['device']['begin']
                x2, y2 = data['device']['end']
                x = [x1, x2]
                y = [y1, y2]
                roi_2d = RectangularROI(
                    xmin=min(x), xmax=max(x), ymin=min(y), ymax=max(y))
                roi = Projected3dROI(roi_2d, self.projection_matrix)
                self.viewer.apply_roi(roi)
