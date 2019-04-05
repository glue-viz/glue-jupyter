import ipymaterialui as mui
from glue.external.echo.selection import ChoiceSeparator


class LinkedDropdown(mui.Div):
    """
    A dropdown widget that is automatically linked to a SelectionCallbackProperty
    and syncs changes both ways.

    * On glue's side the state is in state.<attribute_name>.
    * On the UI the state is in widget_select.value which holds the index of the selected item.
    * Indices are (for the moment) calculated from a list of choices (ignoring separators)
    """

    def __init__(self, state, attribute_name, ui_name=None, label=None):

        super(LinkedDropdown, self).__init__()

        self.state = state
        self.attribute_name = attribute_name

        # FIXME: if the choices change in the SelectionCallbackProperty we should
        # update the Select object.
        self.menu_items = self._create_menu_items()

        # Set up the UI dropdown
        self.widget_select = mui.Select(value=self._get_glue_selected_item_index(),
                                        children=self.menu_items, multiple=False)

        label = label or getattr(type(self.state), self.attribute_name).__doc__
        self.widget_input_label = mui.InputLabel(description=label,
                                                 placeholder='No selection')

        # Note that style is a dict with css key/values
        self.widget_form_control = mui.FormControl(
            children=[self.widget_input_label, self.widget_select], style={'width': '205px'}
        )
        self.child = self.widget_form_control

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
            selected = self._get_choices()[0][self.widget_select.value]
        setattr(self.state, self.attribute_name, selected)

    def _update_ui_from_glue_state(self, *ignore_args):
        """
        Update the UI based on the SelectionCallbackProperty.
        """
        index = self._get_glue_selected_item_index()
        self.widget_select.value = index

    def _get_choices(self):
        """
        Return a list of the choices (excluding separators) in the
        SelectionCallbackProperty.
        """
        choices = []
        labels = []
        display_func = getattr(type(self.state), self.attribute_name).get_display_func(self.state)
        for choice in getattr(type(self.state), self.attribute_name).get_choices(self.state):
            if not isinstance(choice, ChoiceSeparator):
                choices.append(choice)
                labels.append(display_func(choice))
        return choices, labels

    def _create_menu_items(self):
        """
        Generate the MenuItem based on the choices of the
        SelectionCallbackProperty.
        """

        # Get the choices from the SelectionCallbackProperty
        choices, labels = self._get_choices()

        # Generate menu items
        return [mui.MenuItem(description=label, value=index) for index, label in enumerate(labels)]

    def _get_glue_selected_item_index(self):
        """
        Find the numerical index of the currently selected value in the
        SelectionCallbackProperty.
        """

        # Get the chocies from the SelectionCallbackProperty
        choices, labels = self._get_choices()

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
