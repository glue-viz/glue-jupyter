from echo.vue import autoconnect_callbacks_to_vue
from ipywidgets import DOMWidget, widget_serialization

import ipyvolume as ipv
import ipyvuetify as v
import traitlets



__all__ = ['Viewer3DStateWidget']


class Viewer3DStateWidget(v.VuetifyTemplate):
    template_file = (__file__, 'viewer_options_widget.vue')

    has_resolution = traitlets.Bool().tag(sync=True)
    has_figure = traitlets.Bool().tag(sync=True)
    widget_movie_maker = traitlets.Instance(DOMWidget, allow_none=True).tag(sync=True, **widget_serialization)

    def __init__(self, viewer_state):
        super().__init__()

        self.state = viewer_state

        extras = None
        skip = None
        self.has_resolution = hasattr(viewer_state, "resolution")
        if self.has_resolution:
            extras = { "resolution": "selection" }
        else:
            skip = {"resolution"}

        self.has_figure = hasattr(self.state, "figure")
        if self.has_figure:
            self.movie_maker = ipv.moviemaker.MovieMaker(self.state.figure,
                                                    self.state.figure.camera)
            self.widget_movie_maker = self.movie_maker.widget_main

            self.vue_set_movie_maker_visible(False)

        autoconnect_callbacks_to_vue(viewer_state, self, extras=extras, skip=skip)

    def vue_set_movie_maker_visible(self, visible):
        self.widget_movie_maker.layout.display = None if visible else "none"
