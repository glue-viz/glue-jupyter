import bqplot
import ipywidgets as widgets

from glue.viewers.image.state import ImageViewerState

from ...link import link, on_change

from ..view import BqplotBaseView
from ..scatter.layer_artist import BqplotScatterLayerArtist

from .layer_artist import BqplotImageLayerArtist
from ...widgets.linked_dropdown import LinkedDropdown
from ...common.slice_helpers import MultiSliceWidgetHelper


class BqplotImageView(BqplotBaseView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    _state_cls = ImageViewerState
    large_data_size = 2e7

    def __init__(self, session):
        super(BqplotImageView, self).__init__(session)
        on_change([(self.state, 'aspect')])(self._sync_figure_aspect)
        self._sync_figure_aspect()

    def _sync_figure_aspect(self):
        with self.figure.hold_trait_notifications():
            if self.state.aspect == 'equal':
                self.figure.max_aspect_ratio = 1
                self.figure.min_aspect_ratio = 1
            else:
                self.figure.min_aspect_ratio = bqplot.Figure.min_aspect_ratio.default_value
                self.figure.max_aspect_ratio = bqplot.Figure.max_aspect_ratio.default_value

    def get_data_layer_artist(self, layer=None, layer_state=None):
        if layer.ndim == 1:
            cls = BqplotScatterLayerArtist
        else:
            cls = BqplotImageLayerArtist
        return self.get_layer_artist(cls, layer=layer, layer_state=layer_state)

    def get_subset_layer_artist(self, layer=None, layer_state=None):
        if layer.ndim == 1:
            cls = BqplotScatterLayerArtist
        else:
            cls = BqplotImageLayerArtist
        return self.get_layer_artist(cls, layer=layer, layer_state=layer_state)

    def create_tab(self):

        super(BqplotImageView, self).create_tab()

        # Set up dropdowns for main attributes

        self.widget_axis_x = LinkedDropdown(self.state, 'x_att_world', label='x axis')
        self.widget_axis_y = LinkedDropdown(self.state, 'y_att_world', label='y axis')

        # Set up sliders for remaining dimensions

        self.sliders = widgets.VBox()
        self.sliders_helper = MultiSliceWidgetHelper(self.state, self.sliders)

        # Set up additional options

        self.widgets_aspect = widgets.Checkbox(description='Equal aspect ratio')
        aspect_mapping = {'equal': True, 'auto': False}
        aspect_mapping_inverse = {True: 'equal', False: 'auto'}
        link((self.state, 'aspect'), (self.widgets_aspect, 'value'), lambda x: aspect_mapping[x], lambda x: aspect_mapping_inverse[x])

        self.tab_general.children += (self.widget_axis_x, self.widget_axis_y,
                                      self.sliders, self.widgets_aspect,)
