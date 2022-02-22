# A vuetify layout for the glue data viewers. For now we keep this isolated to
# a single file, but once we are happy with it we can just replace the original
# default layout.

import ipyvuetify as v
import traitlets
import ipywidgets as widgets
from ipywidgets import widget_serialization
__all__ = ['vuetify_layout_factory']

shared_layout = widgets.Layout()


class LayoutWidget(v.VuetifyTemplate):
    template_file = (__file__, 'layout_widget.vue')

    controls = traitlets.Dict().tag(sync=True, **widget_serialization)
    drawer_open = traitlets.Bool(False).tag(sync=True)
    open_panels = traitlets.List(default_value=[0, 1]).tag(sync=True)

    def __init__(self, viewer, *args, **kwargs):
        self.layout = shared_layout
        super().__init__(*args, **kwargs)
        self.controls = dict(
            toolbar_selection_tools=viewer.toolbar_selection_tools,
            toolbar_selection_mode=viewer.toolbar_selection_mode,
            toolbar_active_subset=viewer.toolbar_active_subset,
            figure_widget=viewer.figure_widget,
            output_widget=viewer.output_widget,
            viewer_options=viewer.viewer_options,
            layer_options=viewer.layer_options,
        )


def vuetify_layout_factory(viewer):
    return LayoutWidget(viewer)
