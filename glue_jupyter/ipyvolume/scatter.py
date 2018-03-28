import numpy as np
import ipyvolume
import ipywidgets as widgets
import traitlets

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
from ..link import link, calculation, link_component_id_to_select_widget, on_change

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
        if hasattr(self.layer, 'to_mask'):  # TODO: what is the best way to test if it is Data or Subset?
            self.scatter.selected = np.nonzero(self.layer.to_mask())[0]#.tolist()
        self._update_size()

    def _update_size(self):
        size = self.state.size
        scale = self.state.size_scaling / 5  # /5 seems to give similar sizes as the Qt Glue
        if self.state.size_mode == 'Linear':
            size = self.layer.data[self.state.size_att]
            size = (size - self.state.size_vmin) / (self.state.size_vmax - self.state.size_vmin)
            size *= 5
        value = size * scale
        if hasattr(self.layer, 'to_mask'):  # TODO: what is the best way to test if it is Data or Subset?
            self.scatter.size = 0
            self.scatter.size_selected = value
        else:
            self.scatter.size = value
            self.scatter.size_selected = value

    def create_widgets(self):
        widget_visible = widgets.Checkbox(description='visible', value=self.state.visible)
        link((self.state, 'visible'), (widget_visible, 'value'))
        link((self.state, 'visible'), (self.scatter.material, 'visible'))

        self.widget_size = widgets.FloatSlider(description='size', min=0, max=10, value=self.state.size)
        link((self.state, 'size'), (self.widget_size, 'value'))
        self.widget_scaling = widgets.FloatSlider(description='scale', min=0, max=2, value=self.state.size_scaling)
        link((self.state, 'size_scaling'), (self.widget_scaling, 'value'))
        #on_change([self.widget_size, self.widget_scaling])(self._update_size)
        # def set_size(size, scaling):
        #     self.
        #     value = size * scaling / 5
        #     # print('set size', value)
        #     if self.state.size_mode == 'Fixed':
        #         if hasattr(self.layer, 'to_mask'):  # TODO: what is the best way to test if it is Data or Subset?
        #             self.scatter.size = 0
        #             self.scatter.size_selected = value
        #         else:
        #             self.scatter.size = value
        #             self.scatter.size_selected = value

        widget_color = widgets.ColorPicker(description='color')
        link((self.state, 'color'), (widget_color, 'value'))
        link((widget_color, 'value'), (self.scatter, 'color'))
        link((widget_color, 'value'), (self.scatter, 'color_selected'))

        options = type(self.state).size_mode.get_choice_labels(self.state)
        self.widget_size_mode = widgets.RadioButtons(options=options, description='size mode')
        link((self.state, 'size_mode'), (self.widget_size_mode, 'value'))

        helper = self.state.size_att_helper
        self.widget_size_att = widgets.Dropdown(options=[k.label for k in helper.choices],
                                       value=self.state.size_att, description='size')
        link_component_id_to_select_widget(self.state, 'size_att', self.widget_size_att)
        on_change([(self.state, 'size', 'size_scaling', 'size_mode', 'size_vmin', 'size_vmax')])(self._update_size)


        return widgets.VBox([widget_visible, self.widget_size, self.widget_scaling, widget_color, self.widget_size_mode, self.widget_size_att])


