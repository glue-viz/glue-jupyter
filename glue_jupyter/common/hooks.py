from glue.viewers.common.viewer import Viewer
from glue.viewers.common.state import State
import react_ipywidgets as react

def use_echo_state(state: State, name):
    value, set_value = react.use_state(getattr(state, name), key=name)

    def add_event_handler():
        def handler(new_value):
            set_value(new_value)

        def cleanup():
            state.remove_callback(name, handler)

        state.add_callback(name, handler)
        return cleanup

    react.use_side_effect(add_event_handler)

    def set_value_sync(new_value):
        setattr(
            state, name, new_value
        )  # this will update us via add_event_handler, no need to call set_value

    return value, set_value_sync


def use_layer_watch(viewer: Viewer):
    # use a counter to force updates due to external state changes
    counter, set_counter = react.use_state(0)

    def hookup():
        def handler():
            new_counter = counter + 1
            set_counter(new_counter)

        def cleanup():
            viewer._layer_artist_container.change_callbacks.remove(handler)

        viewer._layer_artist_container.on_changed(handler)
        return cleanup

    react.use_side_effect(hookup)
