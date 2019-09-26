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

    template = load_template_as_traitlet(__file__, 'subset_select.vue')

    def __init__(self, viewer):
        super().__init__()

        self.edit_subset_mode = viewer.session.edit_subset_mode
        self.data_collection = viewer.session.data_collection

        def sync_selected_from_state():
            self.selected = [subset_to_dict(subset) for subset in self.edit_subset_mode.edit_subset]

        def sync_available_from_state():
            self.available = [subset_to_dict(subset) for subset in
                              self.data_collection.subset_groups]

        # state change events from glue come in from the hub
        viewer.session.hub.subscribe(self, msg.EditSubsetMessage,
                                     handler=lambda _: sync_selected_from_state())
        viewer.session.hub.subscribe(self, msg.SubsetCreateMessage,
                                     handler=lambda _: sync_available_from_state())

        # manually trigger to set up the initial state
        sync_selected_from_state()
        sync_available_from_state()

    @traitlets.observe('selected')
    def _sync_selected_from_ui(self, change):
        selected_labels = [subset_dict['label'] for subset_dict in change['new']]
        self.edit_subset_mode.edit_subset = [subset for subset in self.data_collection.subset_groups
                                             if subset.label in selected_labels]
