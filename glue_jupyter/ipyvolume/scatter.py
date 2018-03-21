import numpy as np
import ipyvolume
import ipywidgets as widgets
import traitlets
from IPython.display import display

from glue.core.command import ApplySubsetState
from glue.core.layer_artist import LayerArtistBase
from glue.core.state_objects import StateAttributeLimitsHelper
from glue.core.data_combo_helper import ComponentIDComboHelper
from glue.core.roi import PolygonalROI, CircularROI, RectangularROI, Projected3dROI
from glue.core.subset import RoiSubsetState3d
from glue.viewers.scatter.state import ScatterLayerState
from glue.viewers.scatter.state import ScatterViewerState
from glue.viewers.matplotlib.state import (MatplotlibDataViewerState,
                                           MatplotlibLayerState,
                                           DeferredDrawCallbackProperty as DDCProperty,
                                           DeferredDrawSelectionCallbackProperty as DDSCProperty)

from .. import IPyWidgetView
from ..link import link

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
