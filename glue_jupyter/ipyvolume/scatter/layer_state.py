from glue.viewers.scatter3d.layer_state import ScatterLayerState
from echo import CallbackProperty

__all__ = ['Scatter3DLayerState']


class Scatter3DLayerState(ScatterLayerState):
    """
    Scatter layer state with ipyvolume-specific properties.
    """

    geo = CallbackProperty('diamond', docstring="Type of marker")
