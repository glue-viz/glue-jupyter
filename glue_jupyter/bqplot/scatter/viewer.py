from glue.viewers.scatter.state import ScatterViewerState

from ..common.viewer import BqplotBaseView

from .layer_artist import BqplotScatterLayerArtist

from glue.core.units import UnitConverter
from glue.core.subset import roi_to_subset_state

from glue_jupyter.common.state_widgets.layer_scatter import ScatterLayerStateWidget
from glue_jupyter.common.state_widgets.viewer_scatter import ScatterViewerStateWidget

from glue_jupyter.registries import viewer_registry

__all__ = ['BqplotScatterView']


@viewer_registry("scatter")
class BqplotScatterView(BqplotBaseView):

    allow_duplicate_data = False
    allow_duplicate_subset = False

    _state_cls = ScatterViewerState
    _options_cls = ScatterViewerStateWidget
    _data_artist_cls = BqplotScatterLayerArtist
    _subset_artist_cls = BqplotScatterLayerArtist
    _layer_style_widget_cls = ScatterLayerStateWidget

    tools = ['bqplot:home', 'bqplot:panzoom', 'bqplot:rectangle', 'bqplot:circle',
             'bqplot:ellipse', 'bqplot:xrange', 'bqplot:yrange', 'bqplot:polygon', 'bqplot:lasso']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state.add_callback('x_att', self._update_axes)
        self.state.add_callback('y_att', self._update_axes)
        self._update_axes()

    def _update_axes(self, *args):

        if self.state.x_att is not None:
            if self.state.x_display_unit:
                self.state.x_axislabel = str(self.state.x_att) + f' [{self.state.x_display_unit}]'
            else:
                self.state.x_axislabel = str(self.state.x_att)

        if self.state.y_att is not None:
            if self.state.y_display_unit:
                self.state.y_axislabel = str(self.state.y_att) + f' [{self.state.y_display_unit}]'
            else:
                self.state.y_axislabel = str(self.state.y_att)

    def _roi_to_subset_state(self, roi):

        converter = UnitConverter()

        if self.state.x_display_unit:
            xfunc = lambda x: converter.to_native(self.state.x_att.parent,
                                                    self.state.x_att, x,
                                                    self.state.x_display_unit)
        else:
            xfunc = None

        if self.state.y_display_unit:
            yfunc = lambda y: converter.to_native(self.state.y_att.parent,
                                                    self.state.y_att, y,
                                                    self.state.y_display_unit)
        else:
            yfunc = None

        if xfunc or yfunc:
            roi = roi.transformed(xfunc=xfunc, yfunc=yfunc)

        return roi_to_subset_state(roi, x_att=self.state.x_att, y_att=self.state.y_att)
