import ipyvuetify as v

import os
import traitlets
from glue.core import message as msg
from glue.core.hub import HubListener

__all__ = ['SubsetSelect']


def load_template_as_traitlet(path, filename):
    with open(os.path.join(os.path.dirname(path), filename)) as f:
        return traitlets.Unicode(f.read()).tag(sync=True)


def subset_to_dict(subset):
    return {
        'label': subset.label,
        'color': subset.style.color
    }


class SubsetSelect(v.VuetifyTemplate, HubListener):
    """
    Widget responsible for selecting which subsets are active, sync state between UI and glue.
    """

    selected = traitlets.List().tag(sync=True)
    available = traitlets.List().tag(sync=True)
    no_selection_text = traitlets.Unicode('No selection (create new)').tag(sync=True)
    multiple = traitlets.Bool(False).tag(sync=True)
    nr_of_full_names = traitlets.Int(2).tag(sync=True)
    show_allow_multiple_subsets = traitlets.Bool(False).tag(sync=True)

    methods = traitlets.Unicode('''{
        toSubsets(indices) {
            return indices.map(i => this.available[i]);
        },
        deselect() {
            this.multiple = false;
            this.selected = [];
        },
        toggleSubset(index) {
            this.selected = this.selected.includes(index)
                ? this.selected.filter(x => x != index)
                : this.selected.concat(index);
            this.handleMultiple();
        },
        handleMultiple() {
            if (!this.multiple && this.selected.length > 1) {
                this.selected = [this.selected.pop()];
            }
        }
    }''').tag(sync=True)

    template = load_template_as_traitlet(__file__, 'subset_select.vue')

    def __init__(self, session=None):
        super().__init__()

        self.edit_subset_mode = session.edit_subset_mode
        self.data_collection = session.data_collection

        # state change events from glue come in from the hub
        session.hub.subscribe(self, msg.EditSubsetMessage,
                              handler=lambda _: self._sync_selected_from_state())
        session.hub.subscribe(self, msg.SubsetCreateMessage,
                              handler=lambda _: self._sync_available_from_state())
        session.hub.subscribe(self, msg.SubsetDeleteMessage,
                              handler=lambda _: self._sync_available_from_state())

        # manually trigger to set up the initial state
        self._sync_selected_from_state()
        self._sync_available_from_state()

    def _sync_selected_from_state(self):
        self.selected = [self.data_collection.subset_groups.index(subset) for subset
                         in self.edit_subset_mode.edit_subset]

    def _sync_available_from_state(self):
        self.available = [subset_to_dict(subset) for subset in
                          self.data_collection.subset_groups]

    @traitlets.observe('selected')
    def _sync_selected_from_ui(self, change):
        self.edit_subset_mode.edit_subset = [self.data_collection.subset_groups[index] for index in
                                             change['new']]

    @traitlets.observe('multiple')
    def _switch_multiple(self, change):
        if not self.multiple:
            with self.hold_sync():
                if len(self.selected) > 1:
                    # take the first item of the selected items as the single selected item
                    self.selected = self.selected[:1]

    def vue_remove_subset(self, index):
        self.data_collection.remove_subset_group(self.data_collection.subset_groups[index])
