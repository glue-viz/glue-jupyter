import traitlets

from glue.config import colormaps
from glue.core.state_objects import State, CallbackProperty
from echo import SelectionCallbackProperty

from glue_jupyter.vuetify_helpers import _name_to_cmap, link_glue, link_glue_choices


def test_name_to_cmap():
    # Check that a known colormap can be found by name
    _, expected_cmap = colormaps.members[0]
    assert _name_to_cmap(expected_cmap.name) is expected_cmap
    # Check that an unknown name returns None
    assert _name_to_cmap('not_a_real_colormap_name') is None


class SimpleWidget(traitlets.HasTraits):
    value = traitlets.Float(0)


class SimpleState(State):
    value = CallbackProperty(0)


def test_link_glue():
    widget = SimpleWidget()
    state = SimpleState()
    state.value = 5.0

    link_glue(widget, 'value', state)

    # Initial sync from state to widget
    assert widget.value == 5.0

    # State -> widget
    state.value = 10.0
    assert widget.value == 10.0

    # Widget -> state
    widget.value = 20.0
    assert state.value == 20.0


class ChoiceState(State):
    x = SelectionCallbackProperty(default_index=0)


class ChoiceWidget(traitlets.HasTraits):
    x_items = traitlets.List()
    x_selected = traitlets.Any()


def test_link_glue_choices():
    state = ChoiceState()
    ChoiceState.x.set_choices(state, ['a', 'b', 'c'])
    ChoiceState.x.set_display_func(state, lambda x: x.upper())

    widget = ChoiceWidget()
    link_glue_choices(widget, state, 'x')

    # Items should be populated with display labels
    assert len(widget.x_items) == 3
    assert widget.x_items[0] == {'text': 'A', 'value': 0}
    assert widget.x_items[2] == {'text': 'C', 'value': 2}

    # Selected should reflect current state (index 0)
    assert widget.x_selected == 0

    # Changing state selection should update widget
    state.x = 'b'
    assert widget.x_selected == 1

    # Changing widget selection should update state
    widget.x_selected = 2
    assert state.x == 'c'
