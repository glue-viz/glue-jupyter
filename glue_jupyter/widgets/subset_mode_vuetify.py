from contextlib import nullcontext

import glue.core.message as msg
import ipyvuetify as v
import ipywidgets as widgets
from glue.core.edit_subset_mode import AndMode, AndNotMode, OrMode, ReplaceMode, XorMode
from glue.core.hub import HubListener
from glue.icons import icon_path
from glue.utils.decorators import avoid_circular

__all__ = ['SelectionModeMenu']

ICON_WIDTH = 20


def make_lazy(name):
    def make():
        widgets.Image.from_file(icon_path(name, icon_format="svg"),
                                width=ICON_WIDTH)
    return make


icon_replace = make_lazy("glue_replace")
icon_or = make_lazy("glue_or")
icon_and = make_lazy("glue_and")
icon_xor = make_lazy("glue_xor")
icon_andnot = make_lazy("glue_andnot")


class SelectionModeMenu(v.Menu, HubListener):

    def __init__(self, session=None, output_widget=None):

        self.output = output_widget
        self.session = session

        self.modes = [
            ("replace", icon_replace(), ReplaceMode),
            ("add", icon_or(), OrMode),
            ("and", icon_and(), AndMode),
            ("xor", icon_xor(), XorMode),
            ("remove", icon_andnot(), AndNotMode),
        ]

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
        with self.output or nullcontext():
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
        with self.output or nullcontext():
            if self.session.edit_subset_mode.mode != mode:
                self.session.edit_subset_mode.mode = mode
            for m in self.modes:
                if mode is m[2]:
                    icon = m[1]
                    break
            else:
                icon = self.modes[0][1]
            self.main.children = [icon]
