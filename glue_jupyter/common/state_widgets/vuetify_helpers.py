from weakref import ref
from glue.utils import avoid_circular


__all__ = ['link_vuetify_checkbox', 'link_vuetify_button', 'link_vuetify_generic']


class link_vuetify_checkbox:

    connected = True

    def disconnect(self):
        self.connected = False

    def __init__(self, widget, state, attribute):
        self.widget = ref(widget)
        self.state = ref(state)
        self.attribute = attribute
        self.update_widget()
        self.widget().on_event('change', self.update_state)
        self.state().add_callback(self.attribute, self.update_widget)

    @avoid_circular
    def update_state(self, *ignore_args):
        if not self.connected:
            return
        setattr(self.state(), self.attribute, self.widget().v_model)

    @avoid_circular
    def update_widget(self, *ignore_args):
        if not self.connected:
            return
        self.widget().v_model = getattr(self.state(), self.attribute)


class link_vuetify_button:

    connected = True

    def disconnect(self):
        self.connected = False

    def __init__(self, widget, state, attribute):
        self.widget = ref(widget)
        self.state = ref(state)
        self.attribute = attribute
        self.update_widget()
        self.widget().on_event('change', self.update_state)
        self.state().add_callback(self.attribute, self.update_widget)

    @avoid_circular
    def update_state(self, *ignore_args):
        if not self.connected:
            return
        setattr(self.state(), self.attribute, self.widget().v_model)

    @avoid_circular
    def update_widget(self, *ignore_args):
        if not self.connected:
            return
        self.widget().v_model = getattr(self.state(), self.attribute)


class link_vuetify_generic:

    connected = True

    def __init__(self, event, widget, state, attribute, function_to_widget=None, function_to_state=None):
        self.widget = ref(widget)
        self.state = ref(state)
        self.attribute = attribute
        self.function_to_widget = ref(function_to_widget) if function_to_widget is not None else None
        self.function_to_state = ref(function_to_state) if function_to_state is not None else None
        self.update_widget()
        self.widget().on_event(event, self.update_state)
        self.state().add_callback(self.attribute, self.update_widget)

    @avoid_circular
    def update_state(self, *ignore_args):
        if not self.connected:
            return
        if getattr(self.state(), self.attribute) == self.widget().v_model:
            return
        if self.function_to_state:
            setattr(self.state(), self.attribute, self.function_to_state()(self.widget().v_model))
        else:
            setattr(self.state(), self.attribute, self.widget().v_model)

    @avoid_circular
    def update_widget(self, *ignore_args):
        if not self.connected:
            return
        if self.function_to_widget:
            self.widget().v_model = self.function_to_widget()(getattr(self.state(), self.attribute))
        else:
            self.widget().v_model = getattr(self.state(), self.attribute)

    def disconnect(self):
        self.connected = False
