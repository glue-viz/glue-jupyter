from glue.viewers.scatter3d.layer_state import ScatterLayerState3D
from echo import SelectionCallbackProperty

__all__ = ['Scatter3DLayerState']


class Scatter3DLayerState(ScatterLayerState3D):
    """
    Scatter layer state with ipyvolume-specific properties.
    """

    geo = SelectionCallbackProperty(default_index=2, docstring="Type of marker")

    def __init__(self, *args, **kwargs):
        super(Scatter3DLayerState, self).__init__(*args, **kwargs)

        geo_display = {"sphere": "Sphere",
                       "box": "Box",
                       "diamond": "Diamond",
                       "circle_2d": "Circle (2D)"}

        Scatter3DLayerState.geo.set_choices(self, ["sphere", "box", "diamond", "circle_2d"])
        Scatter3DLayerState.geo.set_display_func(self, geo_display.get)
