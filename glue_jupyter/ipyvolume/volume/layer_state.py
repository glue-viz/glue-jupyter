from glue.viewers.volume3d.layer_state import VolumeLayerState3D as VolumeLayerStateBase
from echo import CallbackProperty

__all__ = ['VolumeLayerState']


class VolumeLayerState(VolumeLayerStateBase):

    opacity_scale = CallbackProperty()
    render_method = CallbackProperty()
    lighting = CallbackProperty()
    max_resolution = CallbackProperty()
    clamp_min = CallbackProperty()
    clamp_max = CallbackProperty()

    data_min = CallbackProperty(0)
    data_max = CallbackProperty(1)

    def __init__(self, layer=None, **kwargs):
        super(VolumeLayerState, self).__init__(layer=layer, **kwargs)
        self.opacity_scale = 0.1
        self.render_method = 'NORMAL'
        self.lighting = True
        self.max_resolution = 256
        self.clamp_min = False
        self.clamp_max = False
