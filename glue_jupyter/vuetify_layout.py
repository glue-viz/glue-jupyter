# A vuetify layout for the glue data viewers

import ipyvuetify as v
from ipywidgets import HBox

import glue.core.message as msg
from glue.core.hub import HubListener


class SelectionModeMenu(v.Menu, HubListener):

    def __init__(self, viewer):

        self.session = viewer.session

        self.modes = viewer.toolbar_selection_mode.selection_modes

        items = []
        for mode in self.modes:
            item = v.ListTile(children=[v.ListTileAction(children=[mode[1]]),
                                        v.ListTileTitle(children=[mode[0]])])
            items.append(item)

        for item in items:
            item.on_event('click', self._sync_state_from_ui)

        mylist = v.List(children=items)

        self.main = v.Btn(icon=True,
                          children=[self.modes[0][1]], slot='activator')

        super().__init__(children=[self.main, mylist])

        self.session.hub.subscribe(self, msg.EditSubsetMessage,
                                   handler=self._on_edit_subset_msg)

        self._sync_ui_from_state(self.session.edit_subset_mode.mode)

    def _sync_state_from_ui(self, widget, event, data):
        icon = widget.children[0].children[0]
        self.main.children = [icon]
        for mode in self.modes:
            if icon in mode[1]:
                break
        else:
            mode = self.modes[0]
        self.session.edit_subset_mode.mode = mode

    def _on_edit_subset_msg(self, msg):
        self._sync_ui_from_state(msg.mode)

    def _sync_ui_from_state(self, mode):
        if self.session.edit_subset_mode.mode != mode:
            self.session.edit_subset_mode.mode = mode
        for m in self.modes:
            if mode is m[2]:
                icon = m[1]
        else:
            icon = self.modes[0][1]
        self.main.children = [icon]


def vuetify_layout_factory(viewer):

    def on_click(widget, event, data):
        drawer.v_model = not drawer.v_model

    sidebar_button = v.ToolbarSideIcon()
    sidebar_button.on_event('click', on_click)

    drawer = v.NavigationDrawer(v_model=False, absolute=True, right=True,
                                children=[sidebar_button,
                                          viewer.viewer_options,
                                          viewer.layer_options])

    toolbar_selection_tools = [v.Btn(icon=True, children=[button.children[0]])
                               for button in viewer.toolbar_selection_tools.children]

    toolbar_selection_mode = SelectionModeMenu(viewer)

    toolbar = v.Toolbar(dense=True,
                        children=[v.ToolbarItems(children=toolbar_selection_tools +
                                                          [viewer.toolbar_active_subset,
                                                           toolbar_selection_mode]),
                                  v.Spacer(),
                                  sidebar_button])

    layout = v.Layout(row=True, wrap=True, children=[
        toolbar,
        v.Flex(x12=True,
               children=[viewer.figure_widget]),
        drawer
    ])

    return layout
