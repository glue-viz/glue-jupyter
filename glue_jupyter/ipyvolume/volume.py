import ipyvolume as ipv
import ipywidgets as widgets
import traitlets
from IPython.display import display
import numpy as np

from .scatter import IpyvolumeScatterLayerArtist
from glue_vispy_viewers.common.layer_state import VispyLayerState
from glue.core.data_combo_helper import ComponentIDComboHelper
from glue.external.echo import (CallbackProperty, SelectionCallbackProperty)
from glue.core.roi import PolygonalROI, CircularROI, RectangularROI, Projected3dROI
from glue.core.data import Subset
from glue.core.subset import RoiSubsetState3d
from glue.core.command import ApplySubsetState
from glue.core.exceptions import IncompatibleAttribute

class IpyvolumeLayerState(VispyLayerState):
    attribute = SelectionCallbackProperty()
    def __init__(self, layer=None, **kwargs):
        super(IpyvolumeLayerState, self).__init__(layer=layer)

        if self.layer is not None:

            self.color = self.layer.style.color
            self.alpha = self.layer.style.alpha

        self.att_helper = ComponentIDComboHelper(self, 'attribute')

        self.add_callback('layer', self._on_layer_change)
        if layer is not None:
            self._on_layer_change()

        self.update_from_dict(kwargs)

    def _on_layer_change(self, layer=None):
        if self.layer is None:
            self.att_helper.set_multiple_data([])
        else:
            self.att_helper.set_multiple_data([self.layer])


from glue_vispy_viewers.common.layer_artist import VispyLayerArtist
class IpyvolumeLayerArtist(VispyLayerArtist):
    def __init__(self, ipyvolume_viewer=None, state=None, layer=None, layer_state=None):
        super(IpyvolumeLayerArtist, self).__init__(layer)
        self.layer = layer or layer_state.layer
        self.ipyvolume_viewer = ipyvolume_viewer
        self._viewer_state = ipyvolume_viewer.state
        assert ipyvolume_viewer.state == state
        self.state = layer_state or IpyvolumeLayerState(layer=self.layer)
        if self.state not in self._viewer_state.layers:
            self._viewer_state.layers.append(self.state)

        ipv.figure(self.ipyvolume_viewer.figure)


    def clear(self):
        pass

    def redraw(self):
        pass

    def update(self):
        #print(self.layer)
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
            #print(data, mask)
        else:
            data = self.layer[self.state.attribute]
        #data = self.layer.data[self.state.attribute].astype(np.float32)
        #print(data, data.shape, self.state.attribute)
        finite_mask = np.isfinite(data)
        data_min, data_max = np.percentile(data[finite_mask], 1), np.percentile(data[finite_mask], 99)
        #data_min, data_max = None, None
        self.volume = ipv.volshow(data, data_min=data_min, data_max=data_max)
        

from glue_vispy_viewers.common.viewer_state import Vispy3DViewerState
class IpyvolumeVolumeViewerState(Vispy3DViewerState):
    def __init__(self, **kwargs):
        super(IpyvolumeVolumeViewerState, self).__init__()
        self.add_callback('layers', self._update_attributes)
        self.update_from_dict(kwargs)

    def _update_attributes(self, *args):
        for layer_state in self.layers:
            if getattr(layer_state.layer, 'ndim', None) == 3:
                data = layer_state.layer
                break
        else:
            data = None

        if data is None:
            type(self).x_att.set_choices(self, [])
            type(self).y_att.set_choices(self, [])
            type(self).z_att.set_choices(self, [])

        else:
            z_cid, y_cid, x_cid = data.pixel_component_ids

            type(self).x_att.set_choices(self, [x_cid])
            type(self).y_att.set_choices(self, [y_cid])
            type(self).z_att.set_choices(self, [z_cid])

#from glue_vispy_viewers.common.vispy_data_viewer import BaseVispyViewer
from .. import IPyWidgetView
class IpyvolumeVolumeView(IPyWidgetView):
    allow_duplicate_data = False
    allow_duplicate_subset = False

    _state_cls = IpyvolumeVolumeViewerState
    # _layer_style_widget_cls = {VolumeLayerArtist: IpyvolumeLayerStyleWidget,
 #                               ScatterLayerArtist: IpyvolumeScatterLayerArtist}

    def __init__(self, *args, **kwargs):
        super(IpyvolumeVolumeView, self).__init__(*args, **kwargs)

        self.state = self._state_cls()
        self.figure = ipv.figure(animation_exponent=1.)
        self.figure.on_selection(self.on_selection)

        selectors = ['lasso', 'circle', 'rectangle']
        self.button_action = widgets.ToggleButtons(description='Mode: ', options=[(selector, selector) for selector in selectors],
                                                   icons=["arrows", "pencil-square-o"])
        traitlets.link((self.figure, 'selector'), (self.button_action, 'label'))
        self.button_box = widgets.VBox(
            children=[self.button_action])#, self.box_state_options])
#         self.state.add_callback('y_att', self._update_axes)
#         self.state.add_callback('x_log', self._update_axes)
#         self.state.add_callback('y_log', self._update_axes)

        self.state.add_callback('x_min', self.limits_to_scales)
        self.state.add_callback('x_max', self.limits_to_scales)
        self.state.add_callback('y_min', self.limits_to_scales)
        self.state.add_callback('y_max', self.limits_to_scales)
        self.output_widget = widgets.Output()
        self.main_widget = widgets.VBox(children=[self.button_box, self.figure, self.output_widget])


    def show(self):
        #display(self.main_widget)
        ipv.figure(self.figure)
        ipv.show()

    def on_selection(self, data, other=None):
        with self.output_widget:
            W = np.matrix(self.figure.matrix_world).reshape((4,4))     .T
            P = np.matrix(self.figure.matrix_projection).reshape((4,4)).T
            M = np.dot(P, W)
            if data['device']:
                if data['type'] == 'lasso':
                    region = data['device']
                    vx, vy = zip(*region)
                    roi_2d = PolygonalROI(vx=vx, vy=vy)
                elif data['type'] == 'circle':
                    x1, y1 = data['device']['begin']
                    x2, y2 = data['device']['end']
                    dx = x2 - x1
                    dy = y2 - y1
                    r = (dx**2 + dy**2)**0.5
                    roi_2d = CircularROI(xc=x1, yc=y1, radius=r)
                elif data['type'] == 'rectangle':
                    x1, y1 = data['device']['begin']
                    x2, y2 = data['device']['end']
                    x = [x1, x2]
                    y = [y1, y2]
                    roi_2d = RectangularROI(xmin=min(x), xmax=max(x), ymin=min(y), ymax=max(y))
                roi = Projected3dROI(roi_2d, M)
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

    def get_data_layer_artist(self, layer=None, layer_state=None):
        if layer.ndim == 1:
            cls = IpyvolumeScatterLayerArtist
        else:
            cls = IpyvolumeLayerArtist
        #print('layer', layer, cls)
        return self.get_layer_artist(cls, layer=layer, layer_state=layer_state)
    
    def get_subset_layer_artist(self, layer=None, layer_state=None):
        if layer.ndim == 1:
            cls = IpyvolumeScatterLayerArtist
        else:
            cls = IpyvolumeLayerArtist
        #print('layer', layer, cls)
        return self.get_layer_artist(cls, layer=layer, layer_state=layer_state)

    def redraw(self):
        pass

from glue.viewers.common.qt.data_viewer_with_state import DataViewerWithState
IpyvolumeVolumeView.add_data = DataViewerWithState.add_data
IpyvolumeVolumeView.add_subset = DataViewerWithState.add_subset
#$IpyvolumeVolumeView.get_data_layer_artist = DataViewerWithState.get_data_layer_artist
