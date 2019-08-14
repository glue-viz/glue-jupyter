from ipywidgets import Dropdown
import ipymaterialui as mui
from glue.external.echo.selection import ChoiceSeparator
from glue.utils import avoid_circular

__all__ = ['LinkedDropdown', 'LinkedDropdownMaterial']


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
        if value is not None:
            self.value = value

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


class LinkedDropdownMaterial(mui.FormControl):
    """
    A dropdown widget that is automatically linked to a SelectionCallbackProperty
    and syncs changes both ways (Material UI version)

    * On glue's side the state is in state.<attribute_name>.
    * On the UI the state is in widget_select.value which holds the index of the selected item.
    * Indices are (for the moment) calculated from a list of choices (ignoring separators)
    """

    def __init__(self, state, attribute_name, ui_name=None, label=None):

        if label is None:
            label = ui_name

        self.state = state
        self.attribute_name = attribute_name

        # FIXME: if the choices change in the SelectionCallbackProperty we should
        # update the Select object.
        self.menu_items = self._create_menu_items()

        # Set up the UI dropdown

        self.widget_select = mui.Select(value=self._get_glue_selected_item_index(),
                                        children=self.menu_items, multiple=False)

        self.widget_input_label = mui.InputLabel(children=[label],
                                                 placeholder='No selection')

        super(LinkedDropdownMaterial, self).__init__(children=[self.widget_input_label,
                                                               self.widget_select],
                                                     style={'width': '100%'})

        # Set up callbacks to keep SelectionCallbackProperty and UI in sync
        self.state.add_callback(self.attribute_name, self._update_ui_from_glue_state)
        self.widget_select.observe(self._update_glue_state_from_ui, 'value')

        # Set initial UI state to match SelectionCallbackProperty
        self._update_ui_from_glue_state()

    def _update_glue_state_from_ui(self, change):
        """
        Update the SelectionCallbackProperty based on the UI.
        """
        if self.widget_select.value == '':
            selected = None
        else:
            selected = get_choices(self.state, self.attribute_name)[0][self.widget_select.value]
        setattr(self.state, self.attribute_name, selected)

    def _update_ui_from_glue_state(self, *ignore_args):
        """
        Update the UI based on the SelectionCallbackProperty.
        """
        index = self._get_glue_selected_item_index()
        self.widget_select.value = index

    def _create_menu_items(self):
        """
        Generate the MenuItem based on the choices of the
        SelectionCallbackProperty.
        """

        # Get the choices from the SelectionCallbackProperty
        choices, labels = get_choices(self.state, self.attribute_name)

        # Generate menu items
        return [mui.MenuItem(children=[label], value=index) for index, label in enumerate(labels)]

    def _get_glue_selected_item_index(self):
        """
        Find the numerical index of the currently selected value in the
        SelectionCallbackProperty.
        """

        # Get the chocies from the SelectionCallbackProperty
        choices, labels = get_choices(self.state, self.attribute_name)

        # Find the selected item
        selected = getattr(self.state, self.attribute_name)

        # Find index by looping manually and using is, as using index/== causes
        # issues with ComponentID which return SubsetStates when compared with
        # values
        for k, choice in enumerate(choices):
            if selected is choice:
                return k
        else:
            if isinstance(selected, str):
                # Now try and match by string if the selected value is a string
                for k, label in enumerate(labels):
                    if selected == label:
                        return k
                else:
                    return ''
            else:
                return ''
