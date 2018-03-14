import numpy as np
import bqplot
import ipywidgets as widgets
import ipywidgets.widgets.trait_types as tt
from IPython.display import display
import PIL.Image
import matplotlib.cm
try:
    from io import BytesIO as StringIO # python3
except:
    from StringIO import StringIO # python2

from glue.core.layer_artist import LayerArtistBase
from glue.core.roi import RectangularROI, RangeROI
from glue.core.command import ApplySubsetState
from glue.viewers.image.state import ImageLayerState
from glue.viewers.image.state import ImageViewerState

from ..link import link

# FIXME: monkey patch ipywidget to accept anything
tt.Color.validate = lambda self, obj, value: value



from .. import IPyWidgetView

# def convert_color(color):
#     #if color == 'green':
#     #    return color
#     return '#777'

def _scalar_to_png_data(I, colormap='viridis'):
    colormap = matplotlib.cm.get_cmap(colormap)
    data = colormap(I, bytes=True)
    width, height = data.shape[1], data.shape[0]
    f = StringIO()
    img = PIL.Image.frombuffer("RGBA", (width, height), data, 'raw')
    img.save(f, "png")
    return f.getvalue()



class BqplotImageLayerArtist(LayerArtistBase):
    _layer_state_cls = ImageLayerState

    def __init__(self, view, viewer_state, layer, layer_state):
        super(BqplotImageLayerArtist, self).__init__(layer)
        self.view = view
        self.state = layer_state or self._layer_state_cls(viewer_state=viewer_state,
                                                          layer=self.layer)
        self._viewer_state = viewer_state
        if self.state not in self._viewer_state.layers:
            self._viewer_state.layers.append(self.state)
        data = np.random.random((32, 32))
        
        self.image_widget = widgets.Image(value=_scalar_to_png_data(data), format='png', width=32, height=32)
        self.image_mark = bqplot.Image(image=self.image_widget,
            scales=self.view.scales, x=[0, 1], y=[0, 1])
        self.view.figure.marks = list(self.view.figure.marks) + [self.image_mark]
        #link((self.image, 'colors'), (self.state, 'color'), lambda x: x[0], lambda x: [x])
        #link((self.image, 'default_opacities'), (self.state, 'alpha'), lambda x: x[0], lambda x: [x])
        #link((self.image, 'default_size'), (self.state, 'size'))
        #self.image.observe(self._workaround_unselected_style, 'colors')

        viewer_state.add_callback('x_att', self._update_xy_att)
        viewer_state.add_callback('y_att', self._update_xy_att)

    def _update_xy_att(self, *args):
        self.update()

    def redraw(self):
        pass
        self.update()
        #self.image.x = self.layer[self._viewer_state.x_att]
        #self.image.y = self.layer[self._viewer_state.y_att]

    def clear(self):
        pass

    def _workaround_unselected_style(self, change):
        # see https://github.com/bloomberg/bqplot/issues/606
        if hasattr(self.layer, 'to_mask'):  # TODO: what is the best way to test if it is Data or Subset?
            self.image.unselected_style = {'fill': 'white', 'stroke': 'none'}
            self.image.unselected_style = {'fill': 'none', 'stroke': 'none'}

    def update(self):
        return
        if isinstance(self.layer, Subset):
            try:
                mask = self.layer.to_mask()
            except IncompatibleAttribute:
                # The following includes a call to self.clear()
                self.disable("Subset cannot be applied to this data")
                return
            else:
                self._enabled = True
            # if self.state.subset_mode == 'outline':
            #     data = mask.astype(np.float32)
            # else:
            data = self.layer.data[self.state.attribute].astype(np.float32)
            data *= mask
        else:
            data = self.layer[self.state.attribute]
        # self.image.x = self.layer.data[self._viewer_state.x_att]
        # self.image.y = self.layer.data[self._viewer_state.y_att]
        # if hasattr(self.layer, 'to_mask'):  # TODO: what is the best way to test if it is Data or Subset?
        #     self.image.selected = np.nonzero(self.layer.to_mask())[0].tolist()
        #     self.image.selected_style = {}
        #     self.image.unselected_style = {'fill': 'none', 'stroke': 'none'}
        # else:
        #     self.image.selected = []
        #     self.image.selected_style = {}
        #     self.image.unselected_style = {}
        #     #self.image.selected_style = {'fill': 'none', 'stroke': 'none'}
        #     #self.image.unselected_style = {'fill': 'green', 'stroke': 'none'}


class BqplotImageView(IPyWidgetView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    _state_cls = ImageViewerState
    _data_artist_cls = BqplotImageLayerArtist
    _subset_artist_cls = BqplotImageLayerArtist

    def __init__(self, session):
        super(BqplotImageView, self).__init__(session)
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
        
        actions = ['move', 'brush', 'brush x']#, 'brush y']
        self.interact_map = {}
        self.panzoom = bqplot.PanZoom(scales={'x': [self.scale_x], 'y': [self.scale_y]})
        self.interact_map['move'] = self.panzoom

        self.brush = bqplot.interacts.BrushSelector(x_scale=self.scale_x, y_scale=self.scale_y, color="green")
        self.interact_map['brush'] = self.brush
        self.brush.observe(self.update_brush, "brushing")

        self.brush_x = bqplot.interacts.BrushIntervalSelector(scale=self.scale_x, color="green" )
        self.interact_map['brush x'] = self.brush_x
        self.brush_x.observe(self.update_brush_x, "brushing")

        self.brush_y = bqplot.interacts.BrushIntervalSelector(scale=self.scale_y, color="green" )
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
        layer.image.colors = ['orange']
        return layer

    def receive_message(self, message):
        print("Message received:")
        print("{0}".format(message))
        self.last_msg = message

    def redraw(self):
        pass # print('redraw view', self.state.x_att, self.state.y_att)

from glue.viewers.common.qt.data_viewer_with_state import DataViewerWithState
BqplotImageView.add_data = DataViewerWithState.add_data
BqplotImageView.add_subset = DataViewerWithState.add_subset
BqplotImageView.get_data_layer_artist = DataViewerWithState.get_data_layer_artist
#BqplotScatterView.get_subset_layer_artist = DataViewerWithState.get_data_layer_artist
#BqplotView.get_layer_artist = DataViewerWithState.get_layer_artist
#s = image2d(catalog.id['RAJ2000'], catalog.id['DEJ2000'], dc)
