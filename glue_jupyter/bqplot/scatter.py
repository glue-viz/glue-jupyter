import numpy as np
import bqplot
import ipywidgets as widgets
import ipywidgets.widgets.trait_types as tt
from IPython.display import display

from glue.core.layer_artist import LayerArtistBase
from glue.viewers.scatter.state import ScatterLayerState

from ..link import link

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
        self.scatter = bqplot.Scatter(
            scales=self.view.scales, x=[0, 1], y=[0, 1])
        self.view.figure.marks = list(self.view.figure.marks) + [self.scatter]
        link((self.scatter, 'colors'), (self.state, 'color'), lambda x: x[0], lambda x: [x])
        link((self.state, 'alpha'), (self.scatter, 'default_opacities'), lambda x: [x], lambda x: x[0])
        link((self.scatter, 'default_size'), (self.state, 'size'))
        self.scatter.observe(self._workaround_unselected_style, 'colors')

        viewer_state.add_callback('x_att', self._update_xy_att)
        viewer_state.add_callback('y_att', self._update_xy_att)

    def _update_xy_att(self, *args):
        self.update()

    def redraw(self):
        pass
        self.update()
        #self.scatter.x = self.layer[self._viewer_state.x_att]
        #self.scatter.y = self.layer[self._viewer_state.y_att]

    def clear(self):
        pass

    def _workaround_unselected_style(self, change):
        # see https://github.com/bloomberg/bqplot/issues/606
        if hasattr(self.layer, 'to_mask'):  # TODO: what is the best way to test if it is Data or Subset?
            self.scatter.unselected_style = {'fill': 'white', 'stroke': 'none'}
            self.scatter.unselected_style = {'fill': 'none', 'stroke': 'none'}

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

