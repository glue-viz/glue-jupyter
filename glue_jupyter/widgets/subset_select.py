import ipywidgets as widgets
import ipymaterialui as mui

from glue.core import message as msg
from glue.core.hub import HubListener


class SubsetSelect(mui.Select, HubListener):
    """
    Widget responsible for selecting which subsets are active, sync state
    between UI and glue.

    On glue's side, the state is in `session.edit_subset_mode.edit_subset`. On
    the UI side, the state is in `widget_select.value` (which gets synced to
    the menu items manually).
    """

    def __init__(self, session):
        self.session = session
        self.data_collection = session.data_collection
        self.output = widgets.Output()  # for error msg'es etc
        self.widget_menu_item_select_multiple_checkbox = mui.Switch(checked=False)  # TODO: ->Switch
        self.widget_menu_item_select_multiple_fcl = mui.FormControlLabel(
            control=self.widget_menu_item_select_multiple_checkbox, label="Allow multiple subsets"
        )
        self.widget_menu_item_select_multiple = mui.MenuItem(
            children=[self.widget_menu_item_select_multiple_fcl], click_fix=True, value="ignore"
        )
        self.widget_menu_item_no_active = mui.MenuItem(children=["No selection (create new)"],
                                                       value="new")
        self.widget_menu_items_subsets = []
        self.widget_menu_item_no_active.observe(self._on_click_menu_item_no_active, 'selected')

        super(SubsetSelect, self).__init__(
            children=[self.widget_menu_item_select_multiple, self.widget_menu_item_no_active],
            style={"width": "248px", "margin": "5px"},
            value="new",
        )

        self.widget_menu_item_select_multiple_checkbox.observe(self._switch_multiple, "checked")

        # state change events from glue come in from the hub
        self.session.hub.subscribe(self, msg.EditSubsetMessage,
                                   handler=self._on_edit_subset_msg)
        self.session.hub.subscribe(self, msg.SubsetCreateMessage,
                                   handler=self._on_subset_create_msg)

        # state changes from the UI via this observed trait
        self.observe(self._sync_state_from_ui, "value")

        # manually trigger to set up the initial state
        self._sync_ui_from_state(self.session.edit_subset_mode.edit_subset)

    def _on_edit_subset_msg(self, msg):
        self._sync_ui_from_state(msg.subset)

    def _on_subset_create_msg(self, msg):
        self._sync_ui_from_state(self.session.edit_subset_mode.edit_subset)

    def _on_click_menu_item_no_active(self, change):
        if change.new:
            for item in self.widget_menu_items_subsets:
                item.selected = False
            self.session.edit_subset_mode.edit_subset = []

    def _sync_state_from_ui(self, change):
        # triggered when ui's value changes
        with self.output:
            subsets = []
            value = self.value
            # sync value to menu items, and collect selected subsets
            for item, subset in zip(self.widget_menu_items_subsets,
                                    self.data_collection.subset_groups):
                if self.widget_menu_item_select_multiple_checkbox.checked:
                    selected = item.value in value
                else:
                    selected = item.value == value
                item.selected = selected
                if selected:
                    subsets.append(subset)
            # sync state to glue
            self.session.edit_subset_mode.edit_subset = subsets

    def _switch_multiple(self, change):
        multiple = change.new
        # we assume to toggle from multiple to single selection
        if multiple:
            with self.hold_sync():
                self.multiple = True
                # turn the selected value into a list of selected values
                self.value = [self.value]
        else:
            with self.hold_sync():
                self.multiple = False
                # take the first item of the selected items as the single selected item
                self.value = self.value[0]

    def _sync_ui_from_state(self, subset_groups_selected):
        # this is called when the state in glue is changed, we sync the UI to reflect its state
        with self.output:
            if self.session.edit_subset_mode._edit_subset != subset_groups_selected:
                self.session.edit_subset_mode._edit_subset = subset_groups_selected
            # truncate list when needed
            trunc = len(self.data_collection.subset_groups)
            self.widget_menu_items_subsets = self.widget_menu_items_subsets[:trunc]
            self._updating_subset_menu_items = True
            try:
                values = []
                for i, subset_group in enumerate(self.data_collection.subset_groups):
                    # don't recreate all widgets, reuse them
                    if len(self.widget_menu_items_subsets) <= i:
                        new_menu = mui.MenuItem()
                        self.widget_menu_items_subsets.append(new_menu)
                    menu = self.widget_menu_items_subsets[i]
                    menu.value = i
                    menu.children = [subset_group.label]
                    menu.selected = subset_group in self.session.edit_subset_mode.edit_subset
                    if menu.selected:
                        values.append(i)
                # here we sync the main state of the UI
                # it will trigger the _sync_state_from_ui, which will sync the
                # rest of the menu items
                if self.widget_menu_item_select_multiple_checkbox.checked:
                    self.value = values
                else:
                    assert len(values) in [0, 1]
                    self.value = values[0] if len(values) else "new"

                self.widget_menu_item_no_active.selected = len(subset_groups_selected) == 0

                self.children = [
                    self.widget_menu_item_select_multiple,
                    self.widget_menu_item_no_active,
                ] + self.widget_menu_items_subsets
            finally:
                self._updating_subset_menu_items = False
