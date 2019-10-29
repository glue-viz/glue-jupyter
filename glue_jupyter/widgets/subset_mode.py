import ipywidgets as widgets
import ipymaterialui as mui

from glue.core import message as msg
import glue.icons
from glue.core.edit_subset_mode import OrMode, AndNotMode, AndMode, XorMode, ReplaceMode
from glue.core.hub import HubListener

ICON_WIDTH = 20
icon_replace = widgets.Image.from_file(glue.icons.icon_path("glue_replace", icon_format="svg"),
                                       width=ICON_WIDTH)
icon_or = widgets.Image.from_file(glue.icons.icon_path("glue_or", icon_format="svg"),
                                  width=ICON_WIDTH)
icon_and = widgets.Image.from_file(glue.icons.icon_path("glue_and", icon_format="svg"),
                                   width=ICON_WIDTH)
icon_xor = widgets.Image.from_file(glue.icons.icon_path("glue_xor", icon_format="svg"),
                                   width=ICON_WIDTH)
icon_andnot = widgets.Image.from_file(glue.icons.icon_path("glue_andnot", icon_format="svg"),
                                      width=ICON_WIDTH)


class SubsetMode(mui.ToggleButtonGroup, HubListener):
    """Widget that manages the subset mode (replace/add/and/xor/remove) state between UI and glue state.

    On glue's side, the state is in `session.edit_subset_mode.mode`. On the UI side, the state
    is in `widget_selection_mode.value`

    """

    def __init__(self, session):
        super(SubsetMode, self).__init__()
        self.session = session
        self.selection_modes = [
            ("replace", icon_replace, ReplaceMode),
            ("add", icon_or, OrMode),
            ("and", icon_and, AndMode),
            ("xor", icon_xor, XorMode),
            ("remove", icon_andnot, AndNotMode),
        ]
        super(SubsetMode, self).__init__(
            exclusive=True,
            value=0,
            style={"margin": "4px"},
            children=[
                mui.ToggleButton(children=[icon], value=k)
                for k, (label, icon, mode) in enumerate(self.selection_modes)
            ]
        )

        self.observe(self._sync_state_from_ui, "value")
        self.session.hub.subscribe(self, msg.EditSubsetMessage, handler=self._on_edit_subset_msg)
        self._sync_ui_from_state(self.session.edit_subset_mode.mode)

    def _on_edit_subset_msg(self, msg):
        self._sync_ui_from_state(msg.mode)

    def _sync_ui_from_state(self, mode):
        if self.session.edit_subset_mode.mode != mode:
            self.session.edit_subset_mode.mode = mode
        index = 0
        for i, (__, __, sel_mode) in enumerate(self.selection_modes):
            if mode == sel_mode:
                index = i
        self.value = index

    def _sync_state_from_ui(self, change):
        self.session.edit_subset_mode.mode = self.selection_modes[self.value][2]
