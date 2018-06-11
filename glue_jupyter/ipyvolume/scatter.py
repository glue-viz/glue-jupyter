import numpy as np
import ipyvolume
import ipywidgets as widgets
import traitlets

from glue.core.data import Subset
from glue.core.command import ApplySubsetState
from glue.viewers.common.layer_artist import LayerArtist
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
from ..link import link, dlink, calculation, link_component_id_to_select_widget, on_change

class Scatter3dLayerState(ScatterLayerState):
    vz_att = DDSCProperty(docstring="The attribute to use for the z vector arrow")

    def __init__(self, viewer_state=None, layer=None, **kwargs):
        self.vz_att_helper = ComponentIDComboHelper(self, 'vz_att',
                                                    numeric=True, categorical=False)
        super(Scatter3dLayerState, self).__init__(viewer_state=viewer_state, layer=layer)
        # self.update_from_dict(kwargs)

    def _on_layer_change(self, layer=None):
        super(Scatter3dLayerState, self)._on_layer_change(layer=layer)
        if self.layer is None:
            self.vz_att_helper.set_multiple_data([])
        else:
            self.vz_att_helper.set_multiple_data([self.layer])

class IpyvolumeScatterLayerArtist(LayerArtist):
    _layer_state_cls = Scatter3dLayerState

    def __init__(self, view, viewer_state, layer, layer_state):
        super(IpyvolumeScatterLayerArtist, self).__init__(viewer_state, layer_state=layer_state, layer=layer)
        self.view = view
        self.state = layer_state or self._layer_state_cls(viewer_state=viewer_state,
                                                          layer=self.layer)
        self._viewer_state = viewer_state
        if self.state not in self._viewer_state.layers:
            self._viewer_state.layers.append(self.state)

        self.scatter = ipyvolume.Scatter(x=[0, 1], y=[0, 1], z=[0,1], color='green',
            color_selected='orange', size_selected=7, size=5, geo='sphere')
        self.quiver = ipyvolume.Scatter(x=[0, 1], y=[0, 1], z=[0,1], color='green',
            color_selected='orange', size_selected=7, size=5, geo='arrow', visible=False)
        self.view.figure.scatters = list(self.view.figure.scatters) + [self.scatter, self.quiver]
        #link((self.scatter, 'selected'), (self.quiver, 'selected'))

        viewer_state.add_callback('x_att', self._update_xyz_att)
        viewer_state.add_callback('y_att', self._update_xyz_att)
        viewer_state.add_callback('z_att', self._update_xyz_att)

    def _update_xyz_att(self, *args):
        self.update()

    def redraw(self):
        pass
        #self.update()

    def clear(self):
        pass

    def update(self):
        # we don't use layer, but layer.data to get everything
        self.scatter.x = self.layer.data[self._viewer_state.x_att]
        self.scatter.y = self.layer.data[self._viewer_state.y_att]
        self.scatter.z = self.layer.data[self._viewer_state.z_att]
        self.quiver.x = self.layer.data[self._viewer_state.x_att]
        self.quiver.y = self.layer.data[self._viewer_state.y_att]
        self.quiver.z = self.layer.data[self._viewer_state.z_att]
        if isinstance(self.layer, Subset):
            self.scatter.selected = np.nonzero(self.layer.to_mask())[0]#.tolist()
            self.quiver.selected = np.nonzero(self.layer.to_mask())[0]#.tolist()
        self._update_size()

    def _update_quiver(self):
        with self.quiver.hold_sync():
            self.quiver.vx = self.layer.data[self.state.vx_att]
            self.quiver.vy = self.layer.data[self.state.vy_att]
            self.quiver.vz = self.layer.data[self.state.vz_att]


    def _update_size(self):
        size = self.state.size
        scale = self.state.size_scaling / 5  # /5 seems to give similar sizes as the Qt Glue
        if self.state.size_mode == 'Linear':
            size = self.layer.data[self.state.size_att]
            size = (size - self.state.size_vmin) / (self.state.size_vmax - self.state.size_vmin)
            size *= 5
        value = size * scale
        if isinstance(self.layer, Subset):
            self.scatter.size = 0
            self.scatter.size_selected = value
        else:
            self.scatter.size = value
            self.scatter.size_selected = value

        value = self.state.size * scale * 5
        if isinstance(self.layer, Subset):
            self.quiver.size = 0
            self.quiver.size_selected = value
        else:
            self.quiver.size = value
            self.quiver.size_selected = value


    def create_widgets(self):
        widget_visible = widgets.Checkbox(description='visible', value=self.state.visible)
        link((self.state, 'visible'), (widget_visible, 'value'))
        link((self.state, 'visible'), (self.scatter.material, 'visible'))

        self.widget_size = widgets.FloatSlider(description='size', min=0, max=10, value=self.state.size)
        link((self.state, 'size'), (self.widget_size, 'value'))
        self.widget_scaling = widgets.FloatSlider(description='scale', min=0, max=2, value=self.state.size_scaling)
        link((self.state, 'size_scaling'), (self.widget_scaling, 'value'))

        widget_color = widgets.ColorPicker(description='color')
        link((self.state, 'color'), (widget_color, 'value'))
        link((widget_color, 'value'), (self.scatter, 'color'))
        link((widget_color, 'value'), (self.scatter, 'color_selected'))
        link((widget_color, 'value'), (self.quiver, 'color'))
        link((widget_color, 'value'), (self.quiver, 'color_selected'))

        options = type(self.state).size_mode.get_choice_labels(self.state)
        self.widget_size_mode = widgets.RadioButtons(options=options, description='size mode')
        link((self.state, 'size_mode'), (self.widget_size_mode, 'value'))

        helper = self.state.size_att_helper
        self.widget_size_att = widgets.Dropdown(options=[k.label for k in helper.choices],
                                       value=self.state.size_att, description='size')
        link_component_id_to_select_widget(self.state, 'size_att', self.widget_size_att)
        on_change([(self.state, 'size', 'size_scaling', 'size_mode', 'size_vmin', 'size_vmax')])(self._update_size)

        self.widget_size_vmin = widgets.FloatText()
        self.widget_size_vmax = widgets.FloatText()
        self.widget_size_v = widgets.HBox([widgets.Label(value='limits'), self.widget_size_vmin, self.widget_size_vmax])
        link((self.state, 'size_vmin'), (self.widget_size_vmin, 'value'))
        link((self.state, 'size_vmax'), (self.widget_size_vmax, 'value'))

        dlink((self.widget_size_mode, 'value'), (self.widget_size.layout, 'display'),     lambda value: None if value == options[0] else 'none')
        dlink((self.widget_size_mode, 'value'), (self.widget_size_att.layout, 'display'), lambda value: None if value == options[1] else 'none')
        dlink((self.widget_size_mode, 'value'), (self.widget_size_v.layout, 'display'), lambda value: None if value == options[1] else 'none')

        # vector/quivers
        self.widget_vector = widgets.Checkbox(description='show vectors', value=self.state.vector_visible)

        helper = self.state.vx_att_helper
        self.widget_vector_x = widgets.Dropdown(options=[k.label for k in helper.choices], value=self.state.vx_att, description='vx')
        link_component_id_to_select_widget(self.state, 'vx_att', self.widget_vector_x)

        helper = self.state.vy_att_helper
        self.widget_vector_y = widgets.Dropdown(options=[k.label for k in helper.choices], value=self.state.vy_att, description='vy')
        link_component_id_to_select_widget(self.state, 'vy_att', self.widget_vector_y)

        helper = self.state.vz_att_helper
        self.widget_vector_z = widgets.Dropdown(options=[k.label for k in helper.choices], value=self.state.vz_att, description='vz')
        link_component_id_to_select_widget(self.state, 'vz_att', self.widget_vector_z)

        on_change([(self.state, 'vector_visible', 'vx_att', 'vy_att', 'vz_att')])(self._update_quiver)
        link((self.state, 'vector_visible'), (self.widget_vector, 'value'))
        link((self.state, 'vector_visible'), (self.quiver, 'visible'))
        dlink((self.widget_vector, 'value'), (self.widget_vector_x.layout, 'display'), lambda value: None if value else 'none')
        dlink((self.widget_vector, 'value'), (self.widget_vector_y.layout, 'display'), lambda value: None if value else 'none')
        dlink((self.widget_vector, 'value'), (self.widget_vector_z.layout, 'display'), lambda value: None if value else 'none')

        return widgets.VBox([widget_visible, self.widget_size_mode, self.widget_size, self.widget_size_att, self.widget_size_v, self.widget_scaling, widget_color,
            self.widget_vector, self.widget_vector_x, self.widget_vector_y, self.widget_vector_z])
