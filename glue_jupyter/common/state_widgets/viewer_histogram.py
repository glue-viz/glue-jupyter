import ipyvuetify as v
import traitlets
from ...state_traitlets_helpers import GlueState
from ...vuetify_helpers import load_template, link_glue
from ...widgets.linked_dropdown import get_choices

__all__ = ['HistogramViewerStateWidget']


class HistogramViewerStateWidget(v.VuetifyTemplate):
    template = load_template('viewer_histogram.vue', __file__)
    x_axis = traitlets.List().tag(sync=True)
    selected_axes = traitlets.Unicode().tag(sync=True)
    glue_state = GlueState().tag(sync=True)

    def __init__(self, viewer_state):
        super().__init__()

        self.glue_state = viewer_state

        def update_choices(*args):
            self.x_axis = get_choices(viewer_state, 'x_att')[1]

        viewer_state.add_callback('x_att', update_choices)
        update_choices()

        def get_choice_for_label(label):
            for choice in get_choices(viewer_state, 'x_att')[0]:
                if choice.label == label:
                    return choice

        link_glue(self, 'selected_axes', viewer_state, 'x_att',
                  from_glue_fn = lambda x: x.label,
                  to_glue_fn = get_choice_for_label)
