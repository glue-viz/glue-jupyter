import bqplot
import ipywidgets as widgets
from IPython.display import display

from glue.core.roi import RectangularROI, RangeROI
from glue.core.command import ApplySubsetState

from .. import IPyWidgetView

class BqplotBaseView(IPyWidgetView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    # _state_cls = ImageViewerState
    # _data_artist_cls = BqplotImageLayerArtist
    # _subset_artist_cls = BqplotImageLayerArtist

    def __init__(self, session):
        super(BqplotBaseView, self).__init__(session)
        # session.hub.subscribe(self, SubsetCreateMessage,
        #                       handler=self.receive_message)
        self.state = self._state_cls()

        self.scale_x = bqplot.LinearScale(min=0, max=1)
        self.scale_y = bqplot.LinearScale(min=0, max=1)
        self.scales = {'x': self.scale_x, 'y': self.scale_y}
        self.axis_x = bqplot.Axis(
            scale=self.scale_x, grid_lines='solid', label='x')
        self.axis_y = bqplot.Axis(scale=self.scale_y, orientation='vertical', tick_format='0.2f',
                                  grid_lines='solid', label='y')
        def update_axes(*ignore):
            self.axis_x.label = str(self.state.x_att)
            self.axis_y.label = str(self.state.y_att)
        self.state.add_callback('x_att', update_axes)
        self.state.add_callback('y_att', update_axes)
        self.figure = bqplot.Figure(scales=self.scales, axes=[
                                    self.axis_x, self.axis_y])
        self.figure.padding_y = 0
        
        actions = ['move', 'brush', 'brush x', 'brush y']
        self.interact_map = {}
        self.panzoom = bqplot.PanZoom(scales={'x': [self.scale_x], 'y': [self.scale_y]})
        self.interact_map['move'] = self.panzoom

        self.brush = bqplot.interacts.BrushSelector(x_scale=self.scale_x, y_scale=self.scale_y, color="green")
        self.interact_map['brush'] = self.brush
        self.brush.observe(self.update_brush, "brushing")

        self.brush_x = bqplot.interacts.BrushIntervalSelector(scale=self.scale_x, color="green" )
        self.interact_map['brush x'] = self.brush_x
        self.brush_x.observe(self.update_brush_x, "brushing")

        self.brush_y = bqplot.interacts.BrushIntervalSelector(scale=self.scale_y, color="green", orientation='vertical')
        self.interact_map['brush y'] = self.brush_y
        self.brush_y.observe(self.update_brush_y, "brushing")


        self.button_action = widgets.ToggleButtons(description='Mode: ', options=[(action, action) for action in actions],
                                                   icons=["arrows", "pencil-square-o"])
        self.button_action.observe(self.change_action, "value")
        self.change_action()  # 'fire' manually for intial value

        self.button_box = widgets.HBox(children=[self.button_action])
        self.main_box = widgets.VBox(children=[self.button_box, self.figure])
        


#         self.state.add_callback('y_att', self._update_axes)
#         self.state.add_callback('x_log', self._update_axes)
#         self.state.add_callback('y_log', self._update_axes)

        self.state.add_callback('x_min', self.limits_to_scales)
        self.state.add_callback('x_max', self.limits_to_scales)
        self.state.add_callback('y_min', self.limits_to_scales)
        self.state.add_callback('y_max', self.limits_to_scales)

    @staticmethod
    def update_viewer_state(rec, context):
        print('update viewer state', rec, context)

    def change_action(self, *ignore):
        self.figure.interaction = self.interact_map[self.button_action.value]
        self.brush.selected = []
        self.brush_x.selected = []

    def update_brush(self, *ignore):
        if not self.brush.brushing:  # only select when we ended
            (x1, y1), (x2, y2) = self.brush.selected
            x = [x1, x2]
            y = [y1, y2]
            roi = RectangularROI(xmin=min(x), xmax=max(x), ymin=min(y), ymax=max(y))
            self.apply_roi(roi)

    def update_brush_x(self, *ignore):
        if not self.brush_x.brushing:  # only select when we ended
            x = self.brush_x.selected
            if x is not None and len(x):
                roi = RangeROI(min=min(x), max=max(x), orientation='x')
                self.apply_roi(roi)

    def update_brush_y(self, *ignore):
        if not self.brush_y.brushing:  # only select when we ended
            y = self.brush_y.selected
            if y is not None and len(y):
                roi = RangeROI(min=min(y), max=max(y), orientation='y')
                self.apply_roi(roi)

    def apply_roi(self, roi):
        # TODO: partial copy paste from glue/viewers/matplotlib/qt/data_viewer.py
        if len(self.layers) > 0:
            subset_state = self._roi_to_subset_state(roi)
            cmd = ApplySubsetState(data_collection=self._data,
                                   subset_state=subset_state)
            self._session.command_stack.do(cmd)
        # else:
        #     # Make sure we force a redraw to get rid of the ROI
        #    self.axes.figure.canvas.draw()

    def apply_roi(self, roi):
        if len(self.layers) > 0:
            subset_state = self._roi_to_subset_state(roi)
            cmd = ApplySubsetState(data_collection=self._data,
                                   subset_state=subset_state)
            self._session.command_stack.do(cmd)
        else:
            # Make sure we force a redraw to get rid of the ROI
            self.axes.figure.canvas.draw()

    def _roi_to_subset_state(self, roi):
        # TODO: copy paste from glue/viewers/image/qt/data_viewer.py#L66

        # next lines don't work.. comp has no datetime?
        #x_date = any(comp.datetime for comp in self.state._get_x_components())
        #y_date = any(comp.datetime for comp in self.state._get_y_components())

        #if x_date or y_date:
        #    roi = roi.transformed(xfunc=mpl_to_datetime64 if x_date else None,
        #                          yfunc=mpl_to_datetime64 if y_date else None)

        x_comp = self.state.x_att.parent.get_component(self.state.x_att)
        y_comp = self.state.y_att.parent.get_component(self.state.y_att)

        return x_comp.subset_from_roi(self.state.x_att, roi,
                                      other_comp=y_comp,
                                      other_att=self.state.y_att,
                                      coord='x')

    def show(self):
        display(self.main_box)

    def limits_to_scales(self, *args):
        if self.state.x_min is not None and self.state.x_max is not None:
            self.scale_x.min = float(self.state.x_min)
            self.scale_x.max = float(self.state.x_max)

        if self.state.y_min is not None and self.state.y_max is not None:
            self.scale_y.min = float(self.state.y_min)
            self.scale_y.max = float(self.state.y_max)

    def get_subset_layer_artist(*args, **kwargs):
        layer = DataViewerWithState.get_data_layer_artist(*args, **kwargs)
        return layer

    def receive_message(self, message):
        print("Message received:")
        print("{0}".format(message))
        self.last_msg = message

    def redraw(self):
        pass # print('redraw view', self.state.x_att, self.state.y_att)

    def redraw(self):
        pass



from glue.viewers.common.qt.data_viewer_with_state import DataViewerWithState
BqplotBaseView.add_data = DataViewerWithState.add_data
BqplotBaseView.add_subset = DataViewerWithState.add_subset
BqplotBaseView.get_data_layer_artist = DataViewerWithState.get_data_layer_artist

from glue.viewers.image.state import ImageViewerState
from glue.viewers.scatter.state import ScatterViewerState
from glue.viewers.image.composite_array import CompositeArray

from .image import BqplotImageLayerArtist
from .scatter import BqplotScatterLayerArtist
from ..utils import rgba_to_png_data
import numpy as np

class BqplotImageView(BqplotBaseView):
    allow_duplicate_data = False
    allow_duplicate_subset = False
    _state_cls = ImageViewerState

    def __init__(self, session):
        super(BqplotImageView, self).__init__(session)
        self.composite = CompositeArray()
        data = (np.random.random((32, 32, 4)) * 255).astype(np.uint8)
        self.image_widget = widgets.Image(value=rgba_to_png_data(data), format='png', width=32, height=32)
        self.image_mark = bqplot.Image(image=self.image_widget,
            scales=self.scales, x=[0, 32], y=[0, 32])
        self.figure.marks = list(self.figure.marks) + [self.image_mark]

    def update_composite(self):
        data = self.composite[:,:]
        height, width = data.shape[:2]
        data = (data * 255).astype(np.uint8)
        png_data = rgba_to_png_data(data)
        with self.image_widget.hold_sync():
            self.image_widget.value = png_data
            self.image_widget.width = width
            self.image_widget.height = height
        # force the image mark to update the image data
        self.image_mark.send_state(key='image')
        self.image_mark.x = [0, width]
        self.image_mark.y = [0, height]
        # bug? this will cause a redraw for sure, but why is this needed?
        marks = list(self.figure.marks)
        self.figure.marks = []
        self.figure.marks = marks




    def get_data_layer_artist(self, layer=None, layer_state=None):
        if layer.ndim == 1:
            cls = BqplotScatterLayerArtist
        else:
            cls = BqplotImageLayerArtist
        return self.get_layer_artist(cls, layer=layer, layer_state=layer_state)

    def get_subset_layer_artist(self, layer=None, layer_state=None):
        if layer.ndim == 1:
            cls = BqplotScatterLayerArtist
        else:
            cls = BqplotImageLayerArtist
        return self.get_layer_artist(cls, layer=layer, layer_state=layer_state)


class BqplotScatterView(BqplotBaseView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    _state_cls = ScatterViewerState
    _data_artist_cls = BqplotScatterLayerArtist
    _subset_artist_cls = BqplotScatterLayerArtist
