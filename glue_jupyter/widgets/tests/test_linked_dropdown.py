from glue.core.state_objects import State
from glue.core.data_combo_helper import ComponentIDComboHelper
from echo import SelectionCallbackProperty

from ..linked_dropdown import LinkedDropdown


class DummyState(State):
    """Mock state class for testing only."""

    x_att = SelectionCallbackProperty(docstring='x test attribute')
    y_att = SelectionCallbackProperty(docstring='y test attribute', default_index=-1)


def test_component(app, dataxz, dataxyz):
    # setup
    state = DummyState()
    helper = ComponentIDComboHelper(state, 'x_att', app.data_collection)
    helper.append_data(dataxz)
    state.helper = helper

    # main object we test
    dropdown = LinkedDropdown(state, 'x_att', 'x test attribute')

    # simple sanity tests
    assert dropdown.description == 'x test attribute'
    assert [item[0] for item in dropdown.options] == ['x', 'z']

    # initial state
    assert state.x_att is dataxz.id['x']
    assert dropdown.value is dataxz.id['x']

    # glue state -> ui
    state.x_att = dataxz.id['z']
    assert dropdown.value is dataxz.id['z']

    # ui -> glue state
    dropdown.value = dataxz.id['x']
    assert state.x_att is dataxz.id['x']

    # same, but now be ok with strings
    state.x_att = 'z'
    assert dropdown.value is dataxz.id['z']

    state.x_att = 'x'
    assert dropdown.value is dataxz.id['x']


def test_component_default_index(app, dataxz, dataxyz):

    # Regression test for a bug that caused the incorrect element to be selected
    # when default_index is involved.

    # setup
    state = DummyState()
    helper = ComponentIDComboHelper(state, 'y_att', app.data_collection)
    state.helper = helper
    dropdown = LinkedDropdown(state, 'y_att', 'y test attribute')
    assert [item[0] for item in dropdown.options] == []

    helper.append_data(dataxz)
    assert [item[0] for item in dropdown.options] == ['x', 'z']

    assert state.y_att is dataxz.id['z']
    assert dropdown.value is dataxz.id['z']
