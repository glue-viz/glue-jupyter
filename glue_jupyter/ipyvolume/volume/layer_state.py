from glue.viewers.volume3d.layer_state import VolumeLayerState3D as VolumeLayerStateBase
from echo import CallbackProperty, SelectionCallbackProperty

__all__ = ['VolumeLayerState']


class VolumeLayerState(VolumeLayerStateBase):

    opacity_scale = CallbackProperty()
    render_method = SelectionCallbackProperty()
    lighting = CallbackProperty()
    clamp_min = CallbackProperty()
    clamp_max = CallbackProperty()

    data_min = CallbackProperty(0)
    data_max = CallbackProperty(1)

    def __init__(self, layer=None, **kwargs):
        super(VolumeLayerState, self).__init__(layer=layer, **kwargs)
        VolumeLayerState.render_method.set_choices(self, ["NORMAL", "MAX INTENSITY"])
        self.opacity_scale = 0.5
        self.render_method = 'NORMAL'
        self.lighting = True
        self.clamp_min = False
        self.clamp_max = False
