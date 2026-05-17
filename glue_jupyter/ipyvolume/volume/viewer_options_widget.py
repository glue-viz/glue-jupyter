from echo.vue import autoconnect_callbacks_to_vue
from ipywidgets import DOMWidget, widget_serialization


import ipyvolume as ipv
import ipyvuetify as v
import traitlets

from glue_jupyter.common.slice_helpers import MultiSliceWidgetHelper


__all__ = ["Volume3DViewerStateWidget"]


class Volume3DViewerStateWidget(v.VuetifyTemplate):
    template_file = (__file__, "viewer_options_widget.vue")

    widget_movie_maker = traitlets.Instance(DOMWidget, allow_none=True).tag(sync=True, **widget_serialization)
    widget_slices = traitlets.Instance(DOMWidget, allow_none=True).tag(sync=True, **widget_serialization)

    def __init__(self, viewer_state):
        super().__init__()

        self.state = viewer_state

        self.movie_maker = ipv.moviemaker.MovieMaker(self.state.figure,
                                                     self.state.figure.camera)
        self.widget_movie_maker = self.movie_maker.widget_main
        self.vue_set_movie_maker_visible(False)

        self.slice_helper = MultiSliceWidgetHelper(viewer_state)
        self.widget_slices = self.slice_helper.layout

        autoconnect_callbacks_to_vue(viewer_state, self, extras={"resolution": "selection"})

    def vue_set_movie_maker_visible(self, visible):
        self.widget_movie_maker.layout.display = None if visible else "none"
