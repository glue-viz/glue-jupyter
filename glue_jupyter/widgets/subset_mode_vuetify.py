from contextlib import nullcontext

import ipyvuetify as v
import ipywidgets as widgets

import glue.core.message as msg
from glue.icons import icon_path
from glue.core.edit_subset_mode import OrMode, AndNotMode, AndMode, XorMode, ReplaceMode
from glue.core.hub import HubListener
from glue.utils.decorators import avoid_circular

__all__ = ['SelectionModeMenu']

ICON_WIDTH = 20
icon_replace = widgets.Image.from_file(icon_path("glue_replace", icon_format="svg"),
                                       width=ICON_WIDTH)
icon_or = widgets.Image.from_file(icon_path("glue_or", icon_format="svg"),
                                  width=ICON_WIDTH)
icon_and = widgets.Image.from_file(icon_path("glue_and", icon_format="svg"),
                                   width=ICON_WIDTH)
icon_xor = widgets.Image.from_file(icon_path("glue_xor", icon_format="svg"),
                                   width=ICON_WIDTH)
icon_andnot = widgets.Image.from_file(icon_path("glue_andnot", icon_format="svg"),
                                      width=ICON_WIDTH)


class SelectionModeMenu(v.Menu, HubListener):

    def __init__(self, session=None, output_widget=None):

        self.output = output_widget
        self.session = session

        self.modes = [
            ("replace", icon_replace, ReplaceMode),
            ("add", icon_or, OrMode),
            ("and", icon_and, AndMode),
            ("xor", icon_xor, XorMode),
            ("remove", icon_andnot, AndNotMode),
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
