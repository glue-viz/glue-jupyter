from glue.viewers.image.state import AggregateSlice
from glue.core.coordinate_helpers import world_axis
import ipyvuetify as v
import traitlets
from ...state_traitlets_helpers import GlueState
from ...vuetify_helpers import link_glue_choices


__all__ = ['ImageViewerStateWidget']


class ImageViewerStateWidget(v.VuetifyTemplate):
    template_file = (__file__, 'viewer_image.vue')

    glue_state = GlueState().tag(sync=True)

    color_mode_items = traitlets.List().tag(sync=True)
    color_mode_selected = traitlets.Int(allow_none=True).tag(sync=True)

    reference_data_items = traitlets.List().tag(sync=True)
    reference_data_selected = traitlets.Int(allow_none=True).tag(sync=True)

    x_att_world_items = traitlets.List().tag(sync=True)
    x_att_world_selected = traitlets.Int(allow_none=True).tag(sync=True)

    y_att_world_items = traitlets.List().tag(sync=True)
    y_att_world_selected = traitlets.Int(allow_none=True).tag(sync=True)

    sliders = traitlets.List().tag(sync=True)

    def __init__(self, viewer_state):
        super().__init__()

        self.viewer_state = viewer_state
        self.glue_state = viewer_state

        # Set up dropdown for color mode

        link_glue_choices(self, viewer_state, 'color_mode')

        # Set up dropdown for reference data

        link_glue_choices(self, viewer_state, 'reference_data')

        # Set up dropdowns for main attributes

        link_glue_choices(self, viewer_state, 'x_att_world')
        link_glue_choices(self, viewer_state, 'y_att_world')

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
                                                 )[self.glue_state.slices[i]] if data.coords
                            else '')
        } for i in range(data.ndim) if not used_on_axis(i)]
