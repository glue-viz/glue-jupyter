import numpy as np
import ipyvolume
import ipywidgets as widgets
from IPython.display import display

from glue.core.command import ApplySubsetState
from glue.core.layer_artist import LayerArtistBase
from glue.core.state_objects import StateAttributeLimitsHelper
from glue.core.data_combo_helper import ComponentIDComboHelper
from glue.viewers.scatter.state import ScatterLayerState
from glue.viewers.scatter.state import ScatterViewerState
from glue.viewers.matplotlib.state import (MatplotlibDataViewerState,
                                           MatplotlibLayerState,
                                           DeferredDrawCallbackProperty as DDCProperty,
                                           DeferredDrawSelectionCallbackProperty as DDSCProperty)

from . import IPyWidgetView
from .roi3d import PolygonalProjected3dROI
from .link import link

class Scatter3dLayerState(ScatterLayerState):
    pass

class IpyvolumeScatterLayerArtist(LayerArtistBase):
    _layer_state_cls = Scatter3dLayerState

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
        link((self.scatter, 'color'), (self.state, 'color'))
        link((self.scatter, 'color_selected'), (self.state, 'color'))
        self.state.add_callback('size', lambda *ignore: self.update_selection(), lambda x: x*scale, lambda x: x/scale)

        viewer_state.add_callback('x_att', self._update_xyz_att)
        viewer_state.add_callback('y_att', self._update_xyz_att)
        viewer_state.add_callback('z_att', self._update_xyz_att)

    def _update_xyz_att(self, *args):
        self.update()

    def redraw(self):
        self.update()

    def clear(self):
        pass

    def update(self):
        # we don't use layer, but layer.data to get everything
        self.scatter.x = self.layer.data[self._viewer_state.x_att]
        self.scatter.y = self.layer.data[self._viewer_state.y_att]
        self.scatter.z = self.layer.data[self._viewer_state.z_att]
        self.update_selection()

    def update_selection(self):
        size_scaling = 1./5
        if hasattr(self.layer, 'to_mask'):  # TODO: what is the best way to test if it is Data or Subset?
            self.scatter.selected = np.nonzero(self.layer.to_mask())[0]#.tolist()
            self.scatter.size = 0
            self.scatter.size_selected = self.state.size * size_scaling
        else:
            self.scatter.size = self.state.size * size_scaling
            self.scatter.size_selected = self.state.size * size_scaling


class Scatter3dViewerState(ScatterViewerState):
    z_att = DDSCProperty(docstring='The attribute to show on the z-axis', default_index=2)
    z_min = DDCProperty(docstring='Lower limit of the visible z range')
    z_max = DDCProperty(docstring='Upper limit of the visible z range')
    z_log = DDCProperty(False, docstring='Whether the z axis is logarithmic')

    def __init__(self, **kwargs):
        super(ScatterViewerState, self).__init__()

        self.limits_cache = {}

        self.x_lim_helper = StateAttributeLimitsHelper(self, attribute='x_att',
                                                       lower='x_min', upper='x_max',
                                                       log='x_log',
                                                       limits_cache=self.limits_cache)

        self.y_lim_helper = StateAttributeLimitsHelper(self, attribute='y_att',
                                                       lower='y_min', upper='y_max',
                                                       log='y_log',
                                                       limits_cache=self.limits_cache)
        self.z_lim_helper = StateAttributeLimitsHelper(self, attribute='z_att',
                                                       lower='z_min', upper='z_max',
                                                       log='z_log',
                                                       limits_cache=self.limits_cache)


        self.add_callback('layers', self._layers_changed)

        self.x_att_helper = ComponentIDComboHelper(self, 'x_att', pixel_coord=True, world_coord=True)
        self.y_att_helper = ComponentIDComboHelper(self, 'y_att', pixel_coord=True, world_coord=True)
        self.z_att_helper = ComponentIDComboHelper(self, 'z_att', pixel_coord=True, world_coord=True)

        self.update_from_dict(kwargs)

        self.add_callback('x_log', self._reset_x_limits)
        self.add_callback('y_log', self._reset_y_limits)

    def _layers_changed(self, *args):

        layers_data = self.layers_data
        layers_data_cache = getattr(self, '_layers_data_cache', [])

        if layers_data == layers_data_cache:
            return

        self.x_att_helper.set_multiple_data(self.layers_data)
        self.y_att_helper.set_multiple_data(self.layers_data)
        self.z_att_helper.set_multiple_data(self.layers_data)

        self._layers_data_cache = layers_data

from glue.core.subset import SubsetState
from glue.core.contracts import contract
class RoiSubsetState3d(SubsetState):

    @contract(xatt='isinstance(ComponentID)', yatt='isinstance(ComponentID)', zatt='isinstance(ComponentID)')
    def __init__(self, xatt=None, yatt=None, zatt=None, roi=None):
        super(RoiSubsetState3d, self).__init__()
        self.xatt = xatt
        self.yatt = yatt
        self.zatt = zatt
        self.roi = roi

    @property
    def attributes(self):
        return (self.xatt, self.yatt, self.zatt)

    @contract(data='isinstance(Data)', view='array_view')
    def to_mask(self, data, view=None):

        # TODO: make sure that pixel components don't actually take up much
        #       memory and are just views
        # import IPython
        # IPython.embed()
        x = data[self.xatt, view]
        y = data[self.yatt, view]
        z = data[self.zatt, view]

        # if (x.ndim == data.ndim and
        #     self.xatt in data.pixel_component_ids and
        #     self.yatt in data.pixel_component_ids):

        #     # This is a special case - the ROI is defined in pixel space, so we
        #     # can apply it to a single slice and then broadcast it to all other
        #     # dimensions. We start off by extracting a slice which takes only
        #     # the first elements of all dimensions except the attributes in
        #     # question, for which we take all the elements. We need to preserve
        #     # the dimensionality of the array, hence the use of slice(0, 1).
        #     # Note that we can only do this if the view (if present) preserved
        #     # the dimensionality, which is why we checked that x.ndim == data.ndim

        #     subset = []
        #     for i in range(data.ndim):
        #         if i == self.xatt.axis or i == self.yatt.axis:
        #             subset.append(slice(None))
        #         else:
        #             subset.append(slice(0, 1))

        #     x_slice = x[subset]
        #     y_slice = y[subset]

        #     if self.roi.defined():
        #         result = self.roi.contains(x_slice, y_slice)
        #     else:
        #         result = np.zeros(x_slice.shape, dtype=bool)

        #     result = broadcast_to(result, x.shape)

        # else:
        if 1:
            if self.roi.defined():
                result = self.roi.contains3d(x, y, z)
            else:
                result = np.zeros(x.shape, dtype=bool)

        if result.shape != x.shape:
            raise ValueError("Unexpected error: boolean mask has incorrect dimensions")

        return result

    def copy(self):
        result = RoiSubsetState3d()
        result.xatt = self.xatt
        result.yatt = self.yatt
        result.zatt = self.zatt
        result.roi = self.roi
        return result

class IpyvolumeScatterView(IPyWidgetView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    _state_cls = Scatter3dViewerState
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
        self.figure = ipyvolume.Figure(animation_exponent=1.)
        self.state = self._state_cls()
        self.figure.on_lasso(self.on_lasso)

#         self.state.add_callback('y_att', self._update_axes)
#         self.state.add_callback('x_log', self._update_axes)
#         self.state.add_callback('y_log', self._update_axes)

        self.state.add_callback('x_min', self.limits_to_scales)
        self.state.add_callback('x_max', self.limits_to_scales)
        self.state.add_callback('y_min', self.limits_to_scales)
        self.state.add_callback('y_max', self.limits_to_scales)

        self.output_widget = widgets.Output()
        self.main_widget = widgets.VBox(children=[self.figure, self.output_widget])


    def show(self):
        display(self.main_widget)

    def on_lasso(self, data, other=None):
        with self.output_widget:
            if data['device']:
                #import shapely.geometry
                W = np.matrix(self.figure.matrix_world).reshape((4,4))     .T
                P = np.matrix(self.figure.matrix_projection).reshape((4,4)).T
                M = np.dot(P, W)
                region = data['device']
                vx, vy = zip(*region)
                roi = PolygonalProjected3dROI(vx, vy, M)
                self.apply_roi(roi)

    def apply_roi(self, roi):
        if len(self.layers) > 0:
            x = self.state.x_att # self.state.x_att.parent.get_component(self.state.x_att)
            y = self.state.y_att # self.state.y_att.parent.get_component(self.state.y_att)
            z = self.state.z_att # self.state.z_att.parent.get_component(self.state.z_att)
            subset_state = RoiSubsetState3d(x, y, z, roi)
            cmd = ApplySubsetState(data_collection=self._data,
                                   subset_state=subset_state)
            self._session.command_stack.do(cmd)



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
