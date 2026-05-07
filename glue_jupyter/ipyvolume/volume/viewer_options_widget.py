from echo.vue import autoconnect_callbacks_to_vue
from ipywidgets import DOMWidget, widget_serialization

import ipyvolume as ipv
import ipyvuetify as v
import traitlets


__all__ = ["Volume3DViewerStateWidget"]


class Volume3DViewerStateWidget(v.VuetifyTemplate):
    template_file = (__file__, "viewer_options_widget.vue")

    widget_movie_maker = traitlets.Instance(DOMWidget, allow_none=True).tag(sync=True, **widget_serialization)
    sliders = traitlets.List().tag(sync=True)

    def __init__(self, viewer_state):
        super().__init__()

        self.state = viewer_state

        self.movie_maker = ipv.moviemaker.MovieMaker(self.state.figure,
                                                     self.state.figure.camera)
        self.widget_movie_maker = self.movie_maker.widget_main
        self.vue_set_movie_maker_visible(False)

        autoconnect_callbacks_to_vue(viewer_state, self, extras={"resolution": "selection"})

        for prop in ['x_att', 'y_att', 'z_att', 'slices', 'reference_data']:
            viewer_state.add_callback(prop, self._sync_sliders_from_state)

        self._sync_sliders_from_state()

    def vue_set_movie_maker_visible(self, visible):
        self.widget_movie_maker.layout.display = None if visible else "none"

    def _sync_sliders_from_state(self, *not_used):

        if self.state.reference_data is None or self.state.slices is None:
            return

        if self.state.x_att is None or \
           self.state.y_att is None or \
           self.state.z_att is None:
            return

        data = self.state.reference_data

        def used_on_axis(index):
            return index in [self.state.x_att.axis,
                             self.state.y_att.axis,
                             self.state.z_att.axis]

        new_slices = []
        for i in range(data.ndim):
            slice = self.state.slices[i]
            if not used_on_axis(i) and isinstance(slice, AggregateSlice):
                new_slices.append(slice.center)
            else:
                new_slices.append(slice)
        self.state.slices = tuple(new_slices)

        self.sliders = [{
            'index': i,
            'label': (data.world_component_ids[i].label if data.coords
                      else data.pixel_component_ids[i].label),
            'max': data.shape[i] - 1,
            'unit': (data.get_component(data.world_component_ids[i]).units if data.coords
                     else ''),
            'world_value': ("%0.4E" % world_axis(data.coords,
                                                 data,
                                                 pixel_axis=data.ndim - 1 - i,
                                                 world_axis=data.ndim - 1 - i
                                                 )[self.glue_state.slices[i]] if data.coords
                            else '')
        } for i in range(data.ndim) if not used_on_axis(i)]
