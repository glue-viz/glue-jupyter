import traitlets
from glue.core import Data
from glue.core.state_objects import State, CallbackProperty
from glue.external.echo import ListCallbackProperty
from glue_jupyter.state_traitlets_helpers import GlueState
from glue.viewers.histogram.state import HistogramViewerState, HistogramLayerState


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
    assert widget.latest_json == r'{"a": 1, "b": 2, "sub": []}'
    widget.state.sub.append(CustomSubState())
    assert widget.latest_json == r'{"a": 1, "b": 2, "sub": [{"c": 3}]}'
    widget.state.sub[0].c = 4
    assert widget.latest_json == r'{"a": 1, "b": 2, "sub": [{"c": 4}]}'
    widget.state.b = 5
    assert widget.latest_json == r'{"a": 1, "b": 5, "sub": [{"c": 4}]}'


def test_from_json():
    widget = Widget1()
    widget.state = CustomState()
    widget.state.sub.append(CustomSubState())
    assert widget.latest_json == r'{"a": 1, "b": 2, "sub": [{"c": 3}]}'
    widget.set_state_from_json({"a": 3})
    assert widget.latest_json == r'{"a": 3, "b": 2, "sub": [{"c": 3}]}'
    widget.set_state_from_json({"sub": [{"c": 2}]})
    assert widget.latest_json == r'{"a": 3, "b": 2, "sub": [{"c": 2}]}'


def test_to_json_data():
    # Make sure we just convert the dataset to its label
    widget = Widget1()
    widget.state = CustomState()
    widget.state.a = Data(label='test')
    assert widget.latest_json == r'{"a": "test", "b": 2, "sub": []}'
