
import ipyvuetify as v

import glue.core.message as msg
from glue.core.hub import HubListener
from glue.utils.decorators import avoid_circular

__all__ = ['SelectionModeMenu']


class SelectionModeMenu(v.Menu, HubListener):

    def __init__(self, viewer):

        self.output = viewer.output_widget
        self.session = viewer.session

        self.modes = viewer.toolbar_selection_mode.selection_modes

        items = []
        for mode in self.modes:
            item = v.ListItem(children=[v.ListItemAction(children=[mode[1]]),
                                        v.ListItemTitle(children=[mode[0]])])
            items.append(item)

        for item in items:
            item.on_event('click', self._sync_state_from_ui)

        mylist = v.List(children=items)

        self.main = v.Btn(icon=True,
                          children=[self.modes[0][1]], v_on="menu.on")

        super().__init__(
            v_slots=[{
                'name': 'activator',
                'variable': 'menu',
                'children': self.main
            }],
            children=[mylist])

        self.session.hub.subscribe(self, msg.EditSubsetMessage,
                                   handler=self._on_edit_subset_msg)

        self._sync_ui_from_state(self.session.edit_subset_mode.mode)

    @avoid_circular
    def _sync_state_from_ui(self, widget, event, data):
        with self.output:
            icon = widget.children[0].children[0]
            self.main.children = [icon]
            for mode in self.modes:
                if icon is mode[1]:
                    break
            else:
                mode = self.modes[0]
            self.session.edit_subset_mode.mode = mode[2]

    def _on_edit_subset_msg(self, msg):
        self._sync_ui_from_state(msg.mode)

    @avoid_circular
    def _sync_ui_from_state(self, mode):
        with self.output:
            if self.session.edit_subset_mode.mode != mode:
                self.session.edit_subset_mode.mode = mode
            for m in self.modes:
                if mode is m[2]:
                    icon = m[1]
            else:
                icon = self.modes[0][1]
            self.main.children = [icon]
