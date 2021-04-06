from ipywidgets import Dropdown
from echo.selection import ChoiceSeparator
from glue.utils import avoid_circular

__all__ = ['LinkedDropdown']


def get_choices(state, attribute_name):
    """
    Return a list of the choices (excluding separators) in the
    SelectionCallbackProperty.
    """
    choices = []
    labels = []
    display_func = getattr(type(state), attribute_name).get_display_func(state)
    if display_func is None:
        display_func = str
    for choice in getattr(type(state), attribute_name).get_choices(state):
        if not isinstance(choice, ChoiceSeparator):
            choices.append(choice)
            labels.append(display_func(choice))
    return choices, labels


class LinkedDropdown(Dropdown):
    """
    A dropdown widget that is automatically linked to a SelectionCallbackProperty
    and syncs changes both ways.

    * On glue's side the state is in state.<attribute_name>.
    * On the UI the state is in widget_select.value which holds the index of the selected item.
    * Indices are (for the moment) calculated from a list of choices (ignoring separators)
    """

    def __init__(self, state, attribute_name, ui_name=None, label=None):

        if label is None:
            label = ui_name

        super(LinkedDropdown, self).__init__(description=label)

        self.state = state
        self.attribute_name = attribute_name

        self._update_options()

        self.state.add_callback(self.attribute_name, self._update_ui_from_glue_state)
        self.observe(self._update_glue_state_from_ui, 'value')

        # Set initial UI state to match SelectionCallbackProperty
        self._update_ui_from_glue_state()

    def _update_options(self):
        self._choices, self._labels = get_choices(self.state, self.attribute_name)
        value = self.value
        self.options = list(zip(self._labels, self._choices))
        if value is not None and any(value is choice for choice in self._choices):
            self.value = value
        else:
            self.value = None

    @avoid_circular
    def _update_glue_state_from_ui(self, change):
        """
        Update the SelectionCallbackProperty based on the UI.
        """
        setattr(self.state, self.attribute_name, self.value)

    @avoid_circular
    def _update_ui_from_glue_state(self, *ignore_args):
        """
        Update the UI based on the SelectionCallbackProperty.
        """
        value = getattr(self.state, self.attribute_name)

        # If we are here, the SelectionCallbackProperty has been changed, and
        # this can be due to the options or the selection changing so we need
        # to update the options.
        self._update_options()

        if len(self._choices) > 0:
            value = getattr(self.state, self.attribute_name)
            for choice in self._choices:
                if choice is value:
                    self.value = value
                    break
            else:
                if isinstance(value, str):
                    for i, label in enumerate(self._labels):
                        if label == value:
                            self.value = self._choices[i]
                            break
                    else:
                        self.value = None
                else:
                    self.value = None
