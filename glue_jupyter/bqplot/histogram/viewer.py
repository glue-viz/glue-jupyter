import ipywidgets as widgets

from glue.core.subset import roi_to_subset_state
from glue.core.roi import RangeROI
from glue.viewers.histogram.state import HistogramViewerState

from ...widgets.linked_dropdown import LinkedDropdown

from ...link import link

from ..view import BqplotBaseView

from .layer_artist import BqplotHistogramLayerArtist


class BqplotHistogramView(BqplotBaseView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    _state_cls = HistogramViewerState
    _data_artist_cls = BqplotHistogramLayerArtist
    _subset_artist_cls = BqplotHistogramLayerArtist
    large_data_size = 1e5
    is2d = False

    def create_tab(self):
        super(BqplotHistogramView, self).create_tab()
        self.button_normalize = widgets.ToggleButton(
            value=False, description='normalize', tooltip='Normalize histogram')
        link((self.button_normalize, 'value'), (self.state, 'normalize'))

        self.button_cumulative = widgets.ToggleButton(
            value=False, description='cumulative', tooltip='cumulative histogram')
        link((self.button_cumulative, 'value'), (self.state, 'cumulative'))

        self.widgets_axis = []
        for i, axis_name in enumerate('x'):
            if hasattr(self.state, axis_name + '_att_helper'):
                widget_axis = LinkedDropdown(self.state, axis_name + '_att', label=axis_name + ' axis')
                self.widgets_axis.append(widget_axis)

        # @on_change([(self.state, 'hist_n_bin')])
        # def trigger():

        # self.widget_hist_x_min = widgets.FloatText(description='x min')
        # link((self.state, 'hist_x_min'), (self.widget_hist_x_min, 'value'))

        # self.widget_hist_n_bin = widgets.IntSlider(min=1, max=1000, step=1, description='bins')
        # link((self.state, 'hist_n_bin'), (self.widget_hist_n_bin, 'value'))

        self.tab_general.children += (widgets.HBox([self.button_normalize, self.button_cumulative] ),) + tuple(self.widgets_axis)

    def _roi_to_subset_state(self, roi):
        # TODO: copy paste from glue/viewers/histogram/qt/data_viewer.py
        # TODO Does subset get applied to all data or just visible data?

        bins = self.state.bins

        x = roi.to_polygon()[0]
        lo, hi = min(x), max(x)

        if lo >= bins.min():
            lo = bins[bins <= lo].max()
        if hi <= bins.max():
            hi = bins[bins >= hi].min()

        roi_new = RangeROI(min=lo, max=hi, orientation='x')

        return roi_to_subset_state(roi_new, x_att=self.state.x_att)
