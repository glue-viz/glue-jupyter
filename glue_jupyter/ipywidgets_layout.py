# A vuetify layout for the glue data viewers. For now we keep this isolated to
# a single file, but once we are happy with it we can just replace the original
# default layout.

from ipywidgets import HBox, Tab, VBox


__all__ = ['ipywidgets_layout_factory']


def ipywidgets_layout_factory(viewer):

    # Take all the different widgets and construct a standard layout
    # for the viewers, based on ipywidgets HBox and VBox. This can be
    # overridden in sub-classes to create alternate layouts.

    layout_toolbar = HBox([viewer.toolbar_selection_tools,
                           viewer.toolbar_active_subset,
                           viewer.toolbar_selection_mode])

    layout_tab = Tab([viewer.viewer_options,
                      viewer.layer_options])
    layout_tab.set_title(0, "General")
    layout_tab.set_title(1, "Layers")

    layout = VBox([layout_toolbar,
                   HBox([viewer.figure_widget,
                         layout_tab]),
                   viewer.output_widget])

    return layout
