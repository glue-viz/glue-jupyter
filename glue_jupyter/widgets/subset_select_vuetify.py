import ipyvuetify as v

from glue.core import message as msg
from glue.core.hub import HubListener

__all__ = ['SubsetSelect']


class SubsetSelect(v.Menu, HubListener):
    """
    Widget responsible for selecting which subsets are active, sync state between UI and glue.
    """

    def __init__(self, viewer):

        super().__init__(children=[])

        self.output = viewer.output_widget
        self.session = viewer.session
        self.data_collection = viewer.session.data_collection

        self.main = v.Btn(children=["No selection (create new)"], slot='activator', flat=True)

        self.widget_menu_item_no_active = v.ListTile(children=[v.ListTileTitle(children=["No selection (create new)"])])
        self.widget_menu_item_no_active.on_event('click', self._sync_state_from_ui)

        self.subset_list = v.List(children=[self.widget_menu_item_no_active])

        # state change events from glue come in from the hub
        self.session.hub.subscribe(self, msg.EditSubsetMessage, handler=self._on_edit_subset_msg)
        self.session.hub.subscribe(self, msg.SubsetCreateMessage, handler=self._on_subset_create_msg)

        # state changes from the UI via this observed trait
        self.on_event('change', self._sync_state_from_ui)

        # manually trigger to set up the initial state
        self._sync_ui_from_state(self.session.edit_subset_mode.edit_subset)

        self.children = [self.main, self.subset_list]

    def _on_edit_subset_msg(self, msg):
        self._sync_ui_from_state(msg.subset)

    def _on_subset_create_msg(self, msg):
        self._sync_ui_from_state(self.session.edit_subset_mode.edit_subset)

    def _sync_state_from_ui(self, widget, event, data):

        # triggered when ui's value changes

        with self.output:

            index = self.subset_list.children.index(widget) - 1

            if index < 0:
                self.session.edit_subset_mode.edit_subset = []
            else:
                self.session.edit_subset_mode.edit_subset = [self.data_collection.subset_groups[index]]

    def _sync_ui_from_state(self, subset_groups_selected):

        # this is called when the state in glue is changed, we sync the UI to reflect its state

        with self.output:

            items = [self.widget_menu_item_no_active]

            for i, subset_group in enumerate(self.data_collection.subset_groups):
                # TODO: could avoid re-creating widgets as we do for the material UI version
                item = v.ListTile(children=[v.ListTileTitle(children=[subset_group.label])])
                item.on_event('click', self._sync_state_from_ui)
                items.append(item)

            self.subset_list.children = items

            if self.session.edit_subset_mode.edit_subset:
                self.main.children = [self.session.edit_subset_mode.edit_subset[0].label]
            else:
                self.main.children = ["No selection (create new)"]
