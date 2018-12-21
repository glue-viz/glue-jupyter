import ipymaterialui as mui
import glue.external.echo.selection

# TODO: we probably want to listen to new components being added
# from glue.core import message as msg
# from glue.core.hub import HubListener


class Component(mui.Div):
    """Widget responsible for selecting a component, sync state between UI and a (View)State attribute.

    * On glue's side the state is in state.<attribute_name> and the options are in state.<attribute_name_helper>.
    * On the UI the state is in widget_select.value which holds the index of the selected component.
    * Indices are (for the moment) calculated from a list of components (ignoring separators)
    """

    def __init__(self, state, attribute_name, attribute_name_helper=None, ui_name=None, label=None):
        super(Component, self).__init__()
        self.state = state
        self.attribute_name = attribute_name
        self.attribute_name_helper = attribute_name_helper or self.attribute_name + '_helper'

        self.menu_items = self._create_menu_items()
        self.widget_select = mui.Select(
            value=self._get_glue_selected_component_index(), children=self.menu_items, multiple=False
        )
        label = label or getattr(type(self.state), self.attribute_name).__doc__
        self.widget_input_label = mui.InputLabel(description=label, placeholder='No component')
        # style is a dict with css key/values
        self.widget_form_control = mui.FormControl(
            children=[self.widget_input_label, self.widget_select], style={'width': '205px'}
        )

        self.child = self.widget_form_control

        getattr(type(self.state), self.attribute_name).add_callback(self.state, self._update_ui_from_glue_state)
        self.widget_select.observe(self._update_glue_state_from_ui, 'value')
        # initial state
        self._update_ui_from_glue_state()

    def _update_glue_state_from_ui(self, change):
        component = self._get_components()[self.widget_select.value]
        setattr(self.state, self.attribute_name, component)

    def _update_ui_from_glue_state(self, *ignore_args):
        index = self._get_glue_selected_component_index()
        self.widget_select.value = index

    def _get_components(self):
        return [
            k
            for k in getattr(type(self.state), self.attribute_name).get_choices(self.state)
            if not isinstance(k, glue.external.echo.selection.ChoiceSeparator)
        ]

    def _create_menu_items(self):
        components = self._get_components()
        # we don't use choice_labels, but display_func manually, since we ignore separators for the moment
        display_func = getattr(type(self.state), self.attribute_name).get_display_func(self.state)
        labels = [display_func(components[k]) for k in range(len(components))]
        return [mui.MenuItem(description=label, value=index) for index, label in enumerate(labels)]

    def _get_glue_selected_component_index(self):
        components = self._get_components()
        component = getattr(self.state, self.attribute_name)
        # A users can set a component to a string, and
        # comparing a component to a string always returns a truthy
        if isinstance(component, str):  # WARNING: this will not work for py27
            matches = [k for k in range(len(components)) if component == str(components[k])]
            if len(matches):
                return matches[0]
        try:
            return components.index(component)
        except ValueError:
            # No selection in materialui is equivalent to '' (idea: use None for Python and undefined in js)
            return ''
