import bqplot
from glue.core.layer_artist import LayerArtistBase
from glue.viewers.scatter.state import ScatterLayerState
from glue.viewers.scatter.state import ScatterViewerState
from IPython.display import display
import ipywidgets as widgets
import numpy as np

from . import IPyWidgetView

def _is_traitlet(link):
    return hasattr(link[0], 'observe')
def _is_echo(link):
    return hasattr(getattr(type(link[0]), link[1]), 'add_callback')

class link(object):
    def __init__(self, source, target, f1=lambda x: x, f2=lambda x: x):
        self.source = source
        self.target = target
        
        self._link(source, target, 'source', f1)
        self._link(target, source, 'target', f2, True)

    def _link(self, source, target, name, f, sync_directly=False):
        def sync(*ignore):
            old_value = getattr(target[0], target[1])
            new_value = f(getattr(source[0], source[1]))
            print('old/new', old_value, new_value)
            if new_value != old_value:
                setattr(target[0], target[1], new_value)

        if _is_traitlet(source):
            source[0].observe(sync, source[1])
        elif _is_echo(source):
            callback_property = getattr(type(source[0]), source[1])
            callback_property.add_callback(source[0], sync)
        else:
            raise ValueError('{} is unknown object'.format(name))
        if sync_directly:
            sync()

def convert_color(color):
    #if color == 'green':
    #    return color
    return '#777'

class BqplotScatterLayerArtist(LayerArtistBase):
    _layer_state_cls = ScatterLayerState

    def __init__(self, view, viewer_state, layer, layer_state):
        super(BqplotScatterLayerArtist, self).__init__(layer)
        self.view = view
        self.state = layer_state or self._layer_state_cls(viewer_state=viewer_state,
                                                          layer=self.layer)
        self._viewer_state = viewer_state
        if self.state not in self._viewer_state.layers:
            self._viewer_state.layers.append(self.state)
        self.scatter = bqplot.Scatter(
            scales=self.view.scales, x=[0, 1], y=[0, 1])
        self.view.figure.marks = list(self.view.figure.marks) + [self.scatter]
        link((self.scatter, 'colors'), (self.state, 'color'), lambda x: x[0], lambda x: [convert_color(x)])
        link((self.scatter, 'default_opacities'), (self.state, 'alpha'), lambda x: x[0], lambda x: [x])
        link((self.scatter, 'default_size'), (self.state, 'size'))

    def redraw(self):
        pass
        self.update()
        #self.scatter.x = self.layer[self._viewer_state.x_att]
        #self.scatter.y = self.layer[self._viewer_state.y_att]

    def clear(self):
        pass

    def update(self):
        self.scatter.x = self.layer.data[self._viewer_state.x_att]
        self.scatter.y = self.layer.data[self._viewer_state.y_att]
        if hasattr(self.layer, 'to_mask'):  # TODO: what is the best way to test if it is Data or Subset?
            self.scatter.selected = np.nonzero(self.layer.to_mask())[0].tolist()
            self.scatter.selected_style = {}
            self.scatter.unselected_style = {'fill': 'none', 'stroke': 'none'}
        else:
            self.scatter.selected = []
            self.scatter.selected_style = {}
            self.scatter.unselected_style = {}
            #self.scatter.selected_style = {'fill': 'none', 'stroke': 'none'}
            #self.scatter.unselected_style = {'fill': 'green', 'stroke': 'none'}


class BqplotScatterView(IPyWidgetView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    _state_cls = ScatterViewerState
    _data_artist_cls = BqplotScatterLayerArtist
    _subset_artist_cls = BqplotScatterLayerArtist

    def __init__(self, session):
        super(BqplotScatterView, self).__init__(session)
        # session.hub.subscribe(self, SubsetCreateMessage,
        #                       handler=self.receive_message)
        self.scale_x = bqplot.LinearScale(min=0, max=1)
        self.scale_y = bqplot.LinearScale(min=0, max=1)
        self.scales = {'x': self.scale_x, 'y': self.scale_y}
        self.axis_x = bqplot.Axis(
            scale=self.scale_x, grid_lines='solid', label='X')
        self.axis_y = bqplot.Axis(scale=self.scale_y, orientation='vertical', tick_format='0.2f',
                                  grid_lines='solid', label='Y')
        self.figure = bqplot.Figure(scales=self.scales, axes=[
                                    self.axis_x, self.axis_y])
        
        actions = ['move', 'brush']
        self.interact_map = {}
        self.panzoom = bqplot.PanZoom(scales={'x': [self.scale_x], 'y': [self.scale_y]})
        self.interact_map['move'] = self.panzoom
        self.brush = bqplot.interacts.BrushSelector(x_scale=self.scale_x, y_scale=self.scale_y, color="green")
        self.interact_map['brush'] = self.brush
        self.brush.observe(self.update_brush, "brushing")

        self.button_action = widgets.ToggleButtons(description='', options=[(action, action) for action in actions],
                                                   icons=["arrows", "pencil-square-o"])
        self.button_action.observe(self.change_action, "value")
        self.change_action()  # 'fire' manually for intial value

        self.button_box = widgets.HBox(children=[self.button_action])
        self.main_box = widgets.VBox(children=[self.button_box, self.figure])
        

        self.state = self._state_cls()

#         self.state.add_callback('y_att', self._update_axes)
#         self.state.add_callback('x_log', self._update_axes)
#         self.state.add_callback('y_log', self._update_axes)

        self.state.add_callback('x_min', self.limits_to_scales)
        self.state.add_callback('x_max', self.limits_to_scales)
        self.state.add_callback('y_min', self.limits_to_scales)
        self.state.add_callback('y_max', self.limits_to_scales)

    def change_action(self, *ignore):
        self.figure.interaction = self.interact_map[self.button_action.value]

    def update_brush(self, *ignore):
        print('update brush')
        if not self.brush.brushing:  # only select when we ended
            (x1, y1), (x2, y2) = self.brush.selected
            # TODO: I guess this is not the right way to do the subset
            # data = self.session.data_collection.data[0]
            x = self.state.x_att
            y = self.state.y_att
            # TODO: check what glue qt does, inclusive or exclusive
            # better: roi -> subsetstate -> editsubsetname
            state = (x > x1) & (x < x2) & (y > y1) & (y < y2)
            name = 'brush'
            print(name)
            self.session.data_collection.new_subset_group(name, state)


    def show(self):
        display(self.main_box)

    def limits_to_scales(self, *args):
        if self.state.x_min is not None and self.state.x_max is not None:
            self.scale_x.min = self.state.x_min
            self.scale_x.max = self.state.x_max

        if self.state.y_min is not None and self.state.y_max is not None:
            self.scale_y.min = self.state.y_min
            self.scale_y.max = self.state.y_max

    def get_subset_layer_artist(*args, **kwargs):
        layer = DataViewerWithState.get_data_layer_artist(*args, **kwargs)
        layer.scatter.colors = ['orange']
        return layer

    def receive_message(self, message):
        print("Message received:")
        print("{0}".format(message))
        self.last_msg = message

    def redraw(self):
        pass # print('redraw view', self.state.x_att, self.state.y_att)

from glue.viewers.common.qt.data_viewer_with_state import DataViewerWithState
BqplotScatterView.add_data = DataViewerWithState.add_data
BqplotScatterView.add_subset = DataViewerWithState.add_subset
BqplotScatterView.get_data_layer_artist = DataViewerWithState.get_data_layer_artist
#BqplotScatterView.get_subset_layer_artist = DataViewerWithState.get_data_layer_artist
#BqplotView.get_layer_artist = DataViewerWithState.get_layer_artist
#s = scatter2d(catalog.id['RAJ2000'], catalog.id['DEJ2000'], dc)
