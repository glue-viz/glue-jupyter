import traitlets
from glue.core import Data
from glue.core.state_objects import State, CallbackProperty
from echo import ListCallbackProperty
from glue_jupyter.state_traitlets_helpers import GlueState


class Widget1(traitlets.HasTraits):

    state = GlueState()

    latest_json = None

    # The following two methods mimic the behavior of ipywidgets

    @traitlets.observe('state')
    def on_state_change(self, change):
        to_json = self.trait_metadata('state', 'to_json')
        self.latest_json = to_json(self.state, self)

    def set_state_from_json(self, json):
        from_json = self.trait_metadata('state', 'from_json')
        from_json(json, self)


class CustomSubState(State):
    c = CallbackProperty(3)


class CustomState(State):
    a = CallbackProperty(1)
    b = CallbackProperty(2)
    sub = ListCallbackProperty()


def test_to_json():
    widget = Widget1()
    assert widget.latest_json is None
    widget.state = CustomState()
    assert widget.latest_json == {"a": 1, "b": 2, "sub": []}
    widget.state.sub.append(CustomSubState())
    assert widget.latest_json == {"a": 1, "b": 2, "sub": [{"c": 3}]}
    widget.state.sub[0].c = 4
    assert widget.latest_json == {"a": 1, "b": 2, "sub": [{"c": 4}]}
    widget.state.b = 5
    assert widget.latest_json == {"a": 1, "b": 5, "sub": [{"c": 4}]}
    widget.state.sub.pop(0)
    assert widget.latest_json == {"a": 1, "b": 5, "sub": []}


def test_from_json():
    widget = Widget1()
    widget.state = CustomState()
    widget.state.sub.append(CustomSubState())
    assert widget.latest_json == {"a": 1, "b": 2, "sub": [{"c": 3}]}
    widget.set_state_from_json({"a": 3})
    assert widget.state.a == 3
    assert widget.latest_json == {"a": 3, "b": 2, "sub": [{"c": 3}]}
    widget.set_state_from_json({"sub": [{"c": 2}]})
    assert widget.state.sub[0].c == 2
    assert widget.latest_json == {"a": 3, "b": 2, "sub": [{"c": 2}]}
    # Giving an empty list does not clear the list - it just means that no
    # items will be updated.
    widget.set_state_from_json({"sub": []})
    assert widget.latest_json == {"a": 3, "b": 2, "sub": [{"c": 2}]}
    # We can also update lists by passing a dict with index: value pairs in
    # cases where we just want to update some values
    widget.set_state_from_json({"sub": {0: {'c': 9}}})
    assert widget.latest_json == {"a": 3, "b": 2, "sub": [{"c": 9}]}


def test_to_json_data():
    # Make sure we just convert the dataset to its label
    widget = Widget1()
    widget.state = CustomState()
    widget.state.a = Data(label='test')
    assert widget.latest_json == {"a": "611cfa3b-ebb5-42d2-b5c7-ba9bce8b51a4",
                                  "b": 2,
                                  "sub": []}


def test_from_json_nested_ignore():
    # Regression test for a bug that cause the MAGIC_IGNORE value to be set on
    # the glue state if it existed in a nested structure.
    widget = Widget1()
    widget.state = CustomState()
    widget.state.sub.append(CustomSubState())
    widget.state.sub[0].c = Data(label='test')
    widget.state.sub.append(Data(label='test'))
    assert widget.latest_json == {"a": 1,
                                  "b": 2,
                                  "sub": [{'c': '611cfa3b-ebb5-42d2-b5c7-ba9bce8b51a4'},
                                          '611cfa3b-ebb5-42d2-b5c7-ba9bce8b51a4']}
    widget.set_state_from_json(widget.latest_json)
    assert widget.state.a == 1
    assert widget.state.b == 2
    assert isinstance(widget.state.sub[0].c, Data)
    assert isinstance(widget.state.sub[1], Data)
