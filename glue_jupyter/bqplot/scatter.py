import numpy as np
import bqplot
import ipywidgets as widgets
import ipywidgets.widgets.trait_types as tt
from IPython.display import display

from glue.core.data import Subset
from glue.core.layer_artist import LayerArtistBase
from glue.viewers.scatter.state import ScatterLayerState

from ..link import link, dlink, calculation, link_component_id_to_select_widget, on_change

# FIXME: monkey patch ipywidget to accept anything
tt.Color.validate = lambda self, obj, value: value



from .. import IPyWidgetView

# def convert_color(color):
#     #if color == 'green':
#     #    return color
#     return '#777'

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
        self.scale_size = bqplot.LinearScale()
        self.scale_size_quiver = bqplot.LinearScale()
        self.scale_rotation = bqplot.LinearScale()
        self.scales = dict(**self.view.scales, size=self.scale_size)
        self.scales_quiver = dict(**self.view.scales, size=self.scale_size_quiver, rotation=self.scale_rotation)
        self.scatter = bqplot.Scatter(scales=self.scales, x=[0, 1], y=[0, 1])
        self.quiver = bqplot.Scatter(scales=self.scales_quiver, x=[0, 1], y=[0, 1], visible=False, marker='arrow')
        self.view.figure.marks = list(self.view.figure.marks) + [self.scatter, self.quiver]
        link((self.state, 'color'), (self.scatter, 'colors'), lambda x: [x], lambda x: x[0])
        link((self.state, 'color'), (self.quiver, 'colors'), lambda x: [x], lambda x: x[0])
        link((self.state, 'alpha'), (self.scatter, 'default_opacities'), lambda x: [x], lambda x: x[0])
        self.scatter.observe(self._workaround_unselected_style, 'colors')
        self.quiver.observe(self._workaround_unselected_style, 'colors')

        viewer_state.add_callback('x_att', self._update_xy_att)
        viewer_state.add_callback('y_att', self._update_xy_att)
        self._update_size()

    def _update_xy_att(self, *args):
        self.update()

    def redraw(self):
        pass
        self.update()
        #self.scatter.x = self.layer[self._viewer_state.x_att]
        #self.scatter.y = self.layer[self._viewer_state.y_att]

    def clear(self):
        pass

    def _workaround_unselected_style(self, change=None):
        # see https://github.com/bloomberg/bqplot/issues/606
        if isinstance(self.layer, Subset):
            self.scatter.unselected_style = {'fill': 'white', 'stroke': 'none'}
            self.scatter.unselected_style = {'fill': 'none', 'stroke': 'none'}
            self.quiver.unselected_style = {'fill': 'white', 'stroke': 'none'}
            self.quiver.unselected_style = {'fill': 'none', 'stroke': 'none'}

    def update(self):
        self.scatter.x = self.layer.data[self._viewer_state.x_att]
        self.scatter.y = self.layer.data[self._viewer_state.y_att]
        self.quiver.x = self.layer.data[self._viewer_state.x_att]
        self.quiver.y = self.layer.data[self._viewer_state.y_att]
        if isinstance(self.layer, Subset):
            self.scatter.selected = np.nonzero(self.layer.to_mask())[0].tolist()
            self.scatter.selected_style = {}
            self.scatter.unselected_style = {'fill': 'none', 'stroke': 'none'}
            self.quiver.selected = np.nonzero(self.layer.to_mask())[0].tolist()
            self.quiver.selected_style = {}
            self.quiver.unselected_style = {'fill': 'none', 'stroke': 'none'}
        else:
            self.scatter.selected = []
            self.scatter.selected_style = {}
            self.scatter.unselected_style = {}
            self.quiver.selected = []
            self.quiver.selected_style = {}
            self.quiver.unselected_style = {}
            #self.scatter.selected_style = {'fill': 'none', 'stroke': 'none'}
            #self.scatter.unselected_style = {'fill': 'green', 'stroke': 'none'}

    def _update_quiver(self):
        if not self.state.vector_visible:
            return
        size = 50
        scale = 1
        self.quiver.default_size = int(size * scale * 4) 
        vx = self.layer.data[self.state.vx_att]
        vy = self.layer.data[self.state.vy_att]
        length = np.sqrt(vx**2 + vy**2)
        self.scale_size_quiver.min = np.nanmin(length)
        self.scale_size_quiver.max = np.nanmax(length)
        self.quiver.size = length
        angle = np.arctan2(vy, vx)
        self.scale_rotation.min = -np.pi
        self.scale_rotation.max = np.pi
        self.quiver.rotation = angle

    def create_widgets(self):
        self.widget_visible = widgets.Checkbox(description='visible', value=self.state.visible)
        link((self.state, 'visible'), (self.widget_visible, 'value'))
        link((self.state, 'visible'), (self.scatter, 'visible'))
        return widgets.VBox([self.widget_visible])

    def _update_size(self):
        size = self.state.size
        scale = self.state.size_scaling
        if self.state.size_mode == 'Linear':
            self.scatter.default_size = int(scale * 100) # *50 seems to give similar sizes as the Qt Glue
            self.scatter.size = self.layer.data[self.state.size_att]
            self.scale_size.min = self.state.size_vmin.item()
            self.scale_size.max = self.state.size_vmax.item()
            self._workaround_unselected_style()
        else:
            self.scatter.default_size = int(size * scale * 4) # *4 seems to give similar sizes as the Qt Glue
            self.scatter.size = None

    def create_widgets(self):
        widget_visible = widgets.Checkbox(description='visible', value=self.state.visible)
        link((self.state, 'visible'), (widget_visible, 'value'))
        link((self.state, 'visible'), (self.scatter, 'visible'))

        self.widget_size = widgets.FloatSlider(description='size', min=0, max=10, value=self.state.size)
        link((self.state, 'size'), (self.widget_size, 'value'))
        self.widget_scaling = widgets.FloatSlider(description='scale', min=0, max=2, value=self.state.size_scaling)
        link((self.state, 'size_scaling'), (self.widget_scaling, 'value'))

        widget_color = widgets.ColorPicker(description='color')
        link((self.state, 'color'), (widget_color, 'value'))

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


        self.widget_vector = widgets.Checkbox(description='show vectors', value=self.state.vector_visible)
        helper = self.state.vx_att_helper
        self.widget_vector_x = widgets.Dropdown(options=[k.label for k in helper.choices], value=self.state.vx_att, description='vx')
        link_component_id_to_select_widget(self.state, 'vx_att', self.widget_vector_x)
        helper = self.state.vy_att_helper
        self.widget_vector_y = widgets.Dropdown(options=[k.label for k in helper.choices], value=self.state.vy_att, description='vy')
        link_component_id_to_select_widget(self.state, 'vy_att', self.widget_vector_y)
        on_change([(self.state, 'vector_visible', 'vx_att', 'vy_att')])(self._update_quiver)
        link((self.state, 'vector_visible'), (self.widget_vector, 'value'))
        link((self.state, 'vector_visible'), (self.quiver, 'visible'))
        dlink((self.widget_vector, 'value'), (self.widget_vector_x.layout, 'display'), lambda value: None if value else 'none')
        dlink((self.widget_vector, 'value'), (self.widget_vector_y.layout, 'display'), lambda value: None if value else 'none')


        return widgets.VBox([widget_visible, self.widget_size_mode, self.widget_size, self.widget_size_att, self.widget_size_v, self.widget_scaling, widget_color,
            self.widget_vector, self.widget_vector_x, self.widget_vector_y])
