import numpy as np
import bqplot
import ipywidgets as widgets
import ipywidgets.widgets.trait_types as tt
from IPython.display import display

from glue.core.data import Subset
from glue.core.layer_artist import LayerArtistBase
from glue.viewers.scatter.state import ScatterLayerState
from glue.config import colormaps

from ..link import link, dlink, calculation, link_component_id_to_select_widget, on_change
from ..utils import colormap_to_hexlist

# FIXME: monkey patch ipywidget to accept anything
tt.Color.validate = lambda self, obj, value: value


from .. import IPyWidgetView

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
        self.scale_color = bqplot.ColorScale()
        self.scale_size_quiver = bqplot.LinearScale(min=0, max=1)
        self.scale_rotation = bqplot.LinearScale(min=0, max=1)
        self.scales = dict(self.view.scales, size=self.scale_size, rotation=self.scale_rotation, color=self.scale_color)
        self.scales_quiver = dict(self.view.scales, size=self.scale_size_quiver, rotation=self.scale_rotation)
        self.scatter = bqplot.ScatterMega(scales=self.scales, x=[0, 1], y=[0, 1])
        self.quiver = bqplot.ScatterMega(scales=self.scales_quiver, x=[0, 1], y=[0, 1], visible=False, marker='arrow')
        self.view.figure.marks = list(self.view.figure.marks) + [self.scatter, self.quiver]
        link((self.state, 'color'), (self.scatter, 'colors'), lambda x: [x], lambda x: x[0])
        link((self.state, 'color'), (self.quiver, 'colors'), lambda x: [x], lambda x: x[0])
        self.scatter.observe(self._workaround_unselected_style, 'colors')
        self.quiver.observe(self._workaround_unselected_style, 'colors')

        on_change([(self.state, 'cmap_mode', 'cmap_att')])(self._on_change_cmap_mode_or_att)
        on_change([(self.state, 'cmap')])(self._on_change_cmap)
        link((self.state, 'cmap_vmin'), (self.scale_color, 'min'))
        link((self.state, 'cmap_vmax'), (self.scale_color, 'max'))

        viewer_state.add_callback('x_att', self._update_xy_att)
        viewer_state.add_callback('y_att', self._update_xy_att)
        self._update_size()
        # set initial values for the colormap
        self._on_change_cmap()

    def _update_xy_att(self, *args):
        self.update()

    def _on_change_cmap_mode_or_att(self, ignore=None):
        if self.state.cmap_mode == 'Linear':
            self.scatter.color = self.layer.data[self.state.cmap_att].astype(np.float32)
        else:
            self.scatter.color = None

    def _on_change_cmap(self, ignore=None):
        cmap = self.state.cmap
        colors = colormap_to_hexlist(cmap)
        self.scale_color.colors = colors

    def redraw(self):
        pass
        self.update()

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
        self.scatter.x = self.layer.data[self._viewer_state.x_att].astype(np.float32)
        self.scatter.y = self.layer.data[self._viewer_state.y_att].astype(np.float32)
        self.quiver.x = self.layer.data[self._viewer_state.x_att].astype(np.float32)
        self.quiver.y = self.layer.data[self._viewer_state.y_att].astype(np.float32)
        if isinstance(self.layer, Subset):
            self.scatter.selected = np.nonzero(self.layer.to_mask())[0].tolist()
            self.scatter.selected_style = {}
            self.scatter.unselected_style = {'fill': 'none', 'stroke': 'none'}
            self.quiver.selected = np.nonzero(self.layer.to_mask())[0].tolist()
            self.quiver.selected_style = {}
            self.quiver.unselected_style = {'fill': 'none', 'stroke': 'none'}
        else:
            self.scatter.selected = None
            self.scatter.selected_style = {}
            self.scatter.unselected_style = {}
            self.quiver.selected = None
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
            self.scale_size.min = self.state.size_vmin
            self.scale_size.max = self.state.size_vmax
            self._workaround_unselected_style()
        else:
            self.scatter.default_size = int(size * scale * 4) # *4 seems to give similar sizes as the Qt Glue
            self.scatter.size = None
            self.scale_size.min = 0
            self.scale_size.max = 1

    def create_widgets(self):
        self.widget_visible = widgets.Checkbox(description='visible', value=self.state.visible)
        link((self.state, 'visible'), (self.widget_visible, 'value'))
        link((self.state, 'visible'), (self.scatter, 'visible'))

        self.widget_opacity = widgets.FloatSlider(min=0, max=1, step=0.01, value=self.state.alpha, description='opacity')
        link((self.state, 'alpha'), (self.widget_opacity, 'value'))
        link((self.state, 'alpha'), (self.scatter, 'default_opacities'), lambda x: [x], lambda x: x[0])
        link((self.state, 'alpha'), (self.quiver, 'default_opacities'), lambda x: [x], lambda x: x[0])


        self.widget_size = widgets.FloatSlider(description='size', min=0, max=10, value=self.state.size)
        link((self.state, 'size'), (self.widget_size, 'value'))
        self.widget_scaling = widgets.FloatSlider(description='scale', min=0, max=2, value=self.state.size_scaling)
        link((self.state, 'size_scaling'), (self.widget_scaling, 'value'))

        # color
        self.widget_color = widgets.ColorPicker(description='color')
        link((self.state, 'color'), (self.widget_color, 'value'))

        cmap_mode_options = type(self.state).cmap_mode.get_choice_labels(self.state)
        self.widget_cmap_mode = widgets.RadioButtons(options=cmap_mode_options, description='cmap mode')
        link((self.state, 'cmap_mode'), (self.widget_cmap_mode, 'value'))

        helper = self.state.cmap_att_helper
        self.widget_cmap_att = widgets.Dropdown(options=[k.label for k in helper.choices],
                                       value=self.state.cmap_att, description='color attr.')
        link_component_id_to_select_widget(self.state, 'cmap_att', self.widget_cmap_att)
        # on_change([(self.state, 'cmap', 'cmap_mode', 'cmap_vmin', 'cmap_vmax')])(self._update_cmap)

        self.widget_cmap_vmin = widgets.FloatText(description='color min')
        self.widget_cmap_vmax = widgets.FloatText(description='color max')
        self.widget_cmap_v = widgets.VBox([self.widget_cmap_vmin, self.widget_cmap_vmax])
        link((self.state, 'cmap_vmin'), (self.widget_cmap_vmin, 'value'))
        link((self.state, 'cmap_vmax'), (self.widget_cmap_vmax, 'value'))

        self.widget_cmap = widgets.Dropdown(options=colormaps, description='colormap')
        link((self.state, 'cmap'), (self.widget_cmap, 'label'), lambda cmap: colormaps.name_from_cmap(cmap), lambda name: colormaps[name])

        dlink((self.widget_cmap_mode, 'value'), (self.widget_color.layout, 'display'),     lambda value: None if value == cmap_mode_options[0] else 'none')
        dlink((self.widget_cmap_mode, 'value'), (self.widget_cmap.layout, 'display'),     lambda value: None if value == cmap_mode_options[1] else 'none')
        dlink((self.widget_cmap_mode, 'value'), (self.widget_cmap_att.layout, 'display'), lambda value: None if value == cmap_mode_options[1] else 'none')
        dlink((self.widget_cmap_mode, 'value'), (self.widget_cmap_v.layout, 'display'), lambda value: None if value == cmap_mode_options[1] else 'none')




        # size
        options = type(self.state).size_mode.get_choice_labels(self.state)
        self.widget_size_mode = widgets.RadioButtons(options=options, description='size mode')
        link((self.state, 'size_mode'), (self.widget_size_mode, 'value'))

        helper = self.state.size_att_helper
        self.widget_size_att = widgets.Dropdown(options=[k.label for k in helper.choices],
                                       value=self.state.size_att, description='size')
        link_component_id_to_select_widget(self.state, 'size_att', self.widget_size_att)
        on_change([(self.state, 'size', 'size_scaling', 'size_mode', 'size_vmin', 'size_vmax')])(self._update_size)


        self.widget_size_vmin = widgets.FloatText(description='size min')
        self.widget_size_vmax = widgets.FloatText(description='size min')
        self.widget_size_v = widgets.VBox([self.widget_size_vmin, self.widget_size_vmax])
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


        return widgets.VBox([self.widget_visible, self.widget_opacity,
            self.widget_size_mode, self.widget_size, self.widget_size_att, self.widget_size_v,
            self.widget_cmap_mode, self.widget_color, self.widget_cmap_att, self.widget_cmap_v, self.widget_cmap,
            self.widget_scaling,
            self.widget_vector, self.widget_vector_x, self.widget_vector_y])
