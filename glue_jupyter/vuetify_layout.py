# A vuetify layout for the glue data viewers. For now we keep this isolated to
# a single file, but once we are happy with it we can just replace the original
# default layout.

import ipyvuetify as v

from glue.config import viewer_tool

from glue_jupyter.view import get_viewer_tools
from glue_jupyter.common.toolbar_vuetify import BasicJupyterToolbar
from glue_jupyter.widgets.subset_mode_vuetify import SelectionModeMenu
from glue_jupyter.widgets.subset_select_vuetify import SubsetSelect

__all__ = ['vuetify_layout_factory']


def vuetify_layout_factory(viewer):

    def on_click(widget, event, data):
        drawer.v_model = not drawer.v_model

    sidebar_button = v.AppBarNavIcon()
    sidebar_button.on_event('click', on_click)

    options_panel = v.ExpansionPanels(
        v_model=[0, 1], multiple=True, accordion=True, style_='padding-left: 1px',
        children=[
            v.ExpansionPanel(children=[
                v.ExpansionPanelHeader(class_='font-weight-bold', children=['Viewer Options']),
                v.ExpansionPanelContent(children=[viewer.viewer_options])]),
            v.ExpansionPanel(children=[
                v.ExpansionPanelHeader(class_='font-weight-bold', children=['Layer Options']),
                v.ExpansionPanelContent(children=[viewer.layer_options])])])

    drawer = v.NavigationDrawer(v_model=False, absolute=True, right=True,
                                children=[sidebar_button,
                                          options_panel], width="min-content")

    toolbar_selection_tools = BasicJupyterToolbar(viewer)

    tool_ids, subtool_ids = get_viewer_tools(viewer.__class__)

    if subtool_ids:
        raise ValueError('subtools are not yet supported in Jupyter viewers')

    for tool_id in tool_ids:
        mode_cls = viewer_tool.members[tool_id]
        mode = mode_cls(viewer)
        toolbar_selection_tools.add_tool(mode)

    toolbar_active_subset = SubsetSelect(viewer)

    toolbar_selection_mode = SelectionModeMenu(viewer)

    toolbar = v.Toolbar(dense=True, class_='elevation-0',
                        children=[v.ToolbarItems(children=[toolbar_selection_tools,
                                                           toolbar_selection_mode,
                                                           toolbar_active_subset]),
                                  v.Spacer(),
                                  sidebar_button])

    layout = v.Html(tag='div', children=[
        toolbar,
        v.Row(no_gutters=True, children=[
            v.Col(cols=12, children=[viewer.figure_widget]),
            v.Col(cols=12, children=[viewer.output_widget])
        ]),
        drawer
    ])

    return layout
