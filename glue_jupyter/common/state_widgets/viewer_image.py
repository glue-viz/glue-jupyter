from glue.viewers.image.state import AggregateSlice
from glue.core.coordinate_helpers import world_axis
import ipyvuetify as v
import traitlets

from echo.vue import autoconnect_callbacks_to_vue
from echo.vue._connect import connect_text

__all__ = ['ImageViewerStateWidget']


class ImageViewerStateWidget(v.VuetifyTemplate):
    template_file = (__file__, 'viewer_image.vue')

    sliders = traitlets.List().tag(sync=True)
    slices = traitlets.List().tag(sync=True)

    def __init__(self, viewer_state):
        super().__init__()

        self.viewer_state = viewer_state
        self._updating_slices = False

        autoconnect_callbacks_to_vue(viewer_state, self)

        # aspect is only used in JS expressions, not bound to a known component
        connect_text(viewer_state, 'aspect', self)

        # Set up sliders for remaining dimensions

        for prop in ['x_att', 'y_att', 'slices', 'reference_data']:
            viewer_state.add_callback(prop, self._sync_sliders_from_state)

        self._sync_sliders_from_state()

    def _sync_sliders_from_state(self, *not_used):

        if self.viewer_state.reference_data is None or self.viewer_state.slices is None:
            return

        data = self.viewer_state.reference_data

        def used_on_axis(i):
            return i in [self.viewer_state.x_att.axis, self.viewer_state.y_att.axis]

        new_slices = []
        for i in range(data.ndim):
            if not used_on_axis(i) and isinstance(self.viewer_state.slices[i], AggregateSlice):
                new_slices.append(self.viewer_state.slices[i].center)
            else:
                new_slices.append(self.viewer_state.slices[i])
        self.viewer_state.slices = tuple(new_slices)

        self._updating_slices = True
        try:
            self.slices = list(self.viewer_state.slices)
        finally:
            self._updating_slices = False

        self.sliders = [{
            'index': i,
            'label': (data.world_component_ids[i].label if data.coords
                      else data.pixel_component_ids[i].label),
            'max': data.shape[i]-1,
            'unit': (data.get_component(data.world_component_ids[i]).units if data.coords
                     else ''),
            'world_value': ("%0.4E" % world_axis(data.coords,
                                                 data,
                                                 pixel_axis=data.ndim - 1 - i,
                                                 world_axis=data.ndim - 1 - i
                                                 )[self.viewer_state.slices[i]] if data.coords
                            else '')
        } for i in range(data.ndim) if (not used_on_axis(i) and data.shape[i] > 1)]

    @traitlets.observe('slices')
    def _on_slices_change(self, change):
        if self._updating_slices:
            return
        self._updating_slices = True
        try:
            self.viewer_state.slices = tuple(change['new'])
        finally:
            self._updating_slices = False
