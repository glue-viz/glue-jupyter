import ipyvolume
from glue.core.layer_artist import LayerArtistBase
from glue.viewers.scatter.state import ScatterLayerState
from glue.viewers.scatter.state import ScatterViewerState
from IPython.display import display

from . import IPyWidgetView

class IpyvolumeScatterLayerArtist(LayerArtistBase):
    _layer_state_cls = ScatterLayerState

    def __init__(self, view, viewer_state, layer, layer_state):
        super(IpyvolumeScatterLayerArtist, self).__init__(layer)
        self.view = view
        self.state = layer_state or self._layer_state_cls(viewer_state=viewer_state,
                                                          layer=self.layer)
        self._viewer_state = viewer_state
        if self.state not in self._viewer_state.layers:
            self._viewer_state.layers.append(self.state)

        self.scatter = ipyvolume.Scatter(x=[0, 1], y=[0, 1], z=[0,1], color='green',
            color_selected='orange', size_selected=7, size=5, geo='sphere')
        self.view.figure.scatters = list(self.view.figure.scatters) + [self.scatter]

    def redraw(self):
        self.scatter.x = self.layer[self._viewer_state.x_att]
        self.scatter.y = self.layer[self._viewer_state.y_att]
        self.scatter.z = self.layer[self._viewer_state.y_att]

    def clear(self):
        pass

    def update(self):
        self.scatter.x = self.layer[self._viewer_state.x_att]
        self.scatter.y = self.layer[self._viewer_state.y_att]
        self.scatter.z = self.layer[self._viewer_state.y_att]


class IpyvolumeScatterView(IPyWidgetView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    _state_cls = ScatterViewerState
    _data_artist_cls = IpyvolumeScatterLayerArtist
    _subset_artist_cls = IpyvolumeScatterLayerArtist

    def __init__(self, session):
        super(IpyvolumeScatterView, self).__init__(session)
        # session.hub.subscribe(self, SubsetCreateMessage,
        #                       handler=self.receive_message)
        # self.scale_x = ipyvolume.LinearScale(min=0, max=1)
        # self.scale_y = ipyvolume.LinearScale(min=0, max=1)
        # self.scales = {'x': self.scale_x, 'y': self.scale_y}
        # self.axis_x = ipyvolume.Axis(
        #     scale=self.scale_x, grid_lines='solid', label='X')
        # self.axis_y = ipyvolume.Axis(scale=self.scale_y, orientation='vertical', tick_format='0.2f',
        #                           grid_lines='solid', label='Y')
        self.figure = ipyvolume.Figure()
        self.state = self._state_cls()

#         self.state.add_callback('y_att', self._update_axes)
#         self.state.add_callback('x_log', self._update_axes)
#         self.state.add_callback('y_log', self._update_axes)

        self.state.add_callback('x_min', self.limits_to_scales)
        self.state.add_callback('x_max', self.limits_to_scales)
        self.state.add_callback('y_min', self.limits_to_scales)
        self.state.add_callback('y_max', self.limits_to_scales)

    def show(self):
        display(self.figure)

    def limits_to_scales(self, *args):
        if self.state.x_min is not None and self.state.x_max is not None:
            self.figure.xlim = self.state.x_min, self.state.x_max
        if self.state.y_min is not None and self.state.y_max is not None:
            self.figure.ylim = self.state.y_min, self.state.y_max
        # if self.state.z_min is not None and self.state.z_max is not None:
        #     self.figure.zlim = self.state.z_min, self.state.z_max
        if self.state.y_min is not None and self.state.y_max is not None:
            self.figure.zlim = self.state.y_min, self.state.y_max

    def get_subset_layer_artist(*args, **kwargs):
        layer = DataViewerWithState.get_data_layer_artist(*args, **kwargs)
        layer.scatter.color = 'orange'
        layer.scatter.size = 8
        return layer

    def receive_message(self, message):
        print("Message received:")
        print("{0}".format(message))
        self.last_msg = message

    def redraw(self):
        pass # print('redraw view', self.state.x_att, self.state.y_att)

from glue.viewers.common.qt.data_viewer_with_state import DataViewerWithState
IpyvolumeScatterView.add_data = DataViewerWithState.add_data
IpyvolumeScatterView.add_subset = DataViewerWithState.add_subset
IpyvolumeScatterView.get_data_layer_artist = DataViewerWithState.get_data_layer_artist
#BqplotScatterView.get_subset_layer_artist = DataViewerWithState.get_data_layer_artist
#BqplotView.get_layer_artist = DataViewerWithState.get_layer_artist
#s = scatter2d(catalog.id['RAJ2000'], catalog.id['DEJ2000'], dc)
