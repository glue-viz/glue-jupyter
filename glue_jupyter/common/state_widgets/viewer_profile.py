import ipyvuetify as v

from echo.vue import autoconnect_callbacks_to_vue
from echo.vue._connect import connect_bool

__all__ = ['ProfileViewerStateWidget']


class ProfileViewerStateWidget(v.VuetifyTemplate):
    template_file = (__file__, 'viewer_profile.vue')

    def __init__(self, viewer_state):
        super().__init__()

        self.viewer_state = viewer_state

        autoconnect_callbacks_to_vue(viewer_state, self)

        # Property only used in JS, not bound to a Vue component
        connect_bool(viewer_state, 'normalize', self)
