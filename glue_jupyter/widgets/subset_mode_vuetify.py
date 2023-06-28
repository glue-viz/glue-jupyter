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

MODES = [
    ('replace', 'glue_replace', ReplaceMode),
    ('add', 'glue_or', OrMode),
    ('and', 'glue_and', AndMode),
    ('xor', 'glue_xor', XorMode),
    ('remove', 'glue_andnot', AndNotMode),
]


class SelectionModeMenu(v.Menu, HubListener):

    def __init__(self, session=None, output_widget=None):

        self.output = output_widget
        self.session = session

        self.modes = []
        items = []

        for name, icon_name, mode in MODES:
            icon = widgets.Image.from_file(icon_path(icon_name, icon_format="svg"),
                                           width=ICON_WIDTH)
            self.modes.append((name, icon, mode))

            item = v.ListItem(children=[v.ListItemAction(children=[icon]),
                                        v.ListItemTitle(children=[name])])
            item.on_event('click', self._sync_state_from_ui)
            items.append(item)

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
