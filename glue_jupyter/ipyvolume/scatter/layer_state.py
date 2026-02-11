from glue.viewers.scatter3d.layer_state import ScatterLayerState3D
from echo import CallbackProperty

__all__ = ['Scatter3DLayerState']


class Scatter3DLayerState(ScatterLayerState3D):
    """
    Scatter layer state with ipyvolume-specific properties.
    """

    geo = CallbackProperty('diamond', docstring="Type of marker")
