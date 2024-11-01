import traitlets

from glue_jupyter.state_traitlets_helpers import GlueState
from glue_jupyter.common.state3d import ViewerState3D


class Widget(traitlets.HasTraits):

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


def test_json_serializable():
    widget = Widget()
    assert widget.latest_json is None
    widget.state = ViewerState3D()
    assert widget.latest_json == {
        "x_att": None, "x_min": 0, "x_max": 1,
        "y_att": None, "y_min": 0, "y_max": 1,
        "z_att": None, "z_min": 0, "z_max": 1,
        "visible_axes": True, "native_aspect": False,
        "layers": [], "title": None,
    }
