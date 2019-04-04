from glue.viewers.scatter.state import ScatterViewerState

import glue_jupyter.widgets.component
from ..view import BqplotBaseView

from .layer_artist import BqplotScatterLayerArtist


class BqplotScatterView(BqplotBaseView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    _state_cls = ScatterViewerState
    _data_artist_cls = BqplotScatterLayerArtist
    _subset_artist_cls = BqplotScatterLayerArtist
    large_data_size = 1e7

    def create_tab(self):
        super(BqplotScatterView, self).create_tab()
        self.widgets_axis = []
        for i, axis_name in enumerate('xy'):
            if hasattr(self.state, axis_name + '_att_helper'):
                widget_axis = glue_jupyter.widgets.component.Component(
                    self.state, axis_name + '_att', label=axis_name + ' axis'
                )
                self.widgets_axis.append(widget_axis)
        self.tab_general.children += tuple(self.widgets_axis)
