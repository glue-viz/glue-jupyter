from glue.utils import avoid_circular


__all__ = ['link_vuetify_checkbox', 'link_vuetify_button']


class link_vuetify_checkbox:

    def __init__(self, widget, state, attribute):
        self.widget = widget
        self.state = state
        self.attribute = attribute
        self.update_widget()
        self.widget.on_event('change', self.update_state)
        self.state.add_callback(self.attribute, self.update_widget)

    @avoid_circular
    def update_state(self, *ignore_args):
        setattr(self.state, self.attribute, self.widget.v_model)

    @avoid_circular
    def update_widget(self, *ignore_args):
        self.widget.v_model = getattr(self.state, self.attribute)


class link_vuetify_button:

    def __init__(self, widget, state, attribute):
        self.widget = widget
        self.state = state
        self.attribute = attribute
        self.update_widget()
        self.widget.on_event('click', self.update_state)
        self.state.add_callback(self.attribute, self.update_widget)

    @avoid_circular
    def update_state(self, *ignore_args):
        setattr(self.state, self.attribute, self.widget.v_model)

    @avoid_circular
    def update_widget(self, *ignore_args):
        self.widget.v_model = getattr(self.state, self.attribute)
