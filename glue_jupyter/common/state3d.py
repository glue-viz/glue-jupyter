from glue.viewers.common.state import ViewerState
from echo import (CallbackProperty, SelectionCallbackProperty)
from glue.core.data_combo_helper import ComponentIDComboHelper
from glue.core.state_objects import StateAttributeLimitsHelper
from glue.utils import nonpartial

__all__ = ['ViewerState3D', 'VolumeViewerState', 'Scatter3DViewerState']


class ViewerState3D(ViewerState):
    """
    A common state object for all 3D viewers
    """

    x_att = SelectionCallbackProperty()
    x_min = CallbackProperty(0)
    x_max = CallbackProperty(1)
    # x_stretch = CallbackProperty(1.)

    y_att = SelectionCallbackProperty(default_index=1)
    y_min = CallbackProperty(0)
    y_max = CallbackProperty(1)
    # y_stretch = CallbackProperty(1.)

    z_att = SelectionCallbackProperty(default_index=2)
    z_min = CallbackProperty(0)
    z_max = CallbackProperty(1)
    # z_stretch = CallbackProperty(1.)

    visible_axes = CallbackProperty(True)
    # perspective_view = CallbackProperty(False)
    # clip_data = CallbackProperty(False)
    # native_aspect = CallbackProperty(False)

    limits_cache = CallbackProperty()

    # def _update_priority(self, name):
    #     if name == 'layers':
    #         return 2
    #     elif name.endswith(('_min', '_max')):
    #         return 0
    #     else:
    #         return 1

    def __init__(self, **kwargs):

        super(ViewerState3D, self).__init__(**kwargs)

        if self.limits_cache is None:
            self.limits_cache = {}

        self.x_lim_helper = StateAttributeLimitsHelper(self, attribute='x_att',
                                                       lower='x_min', upper='x_max',
                                                       cache=self.limits_cache)

        self.y_lim_helper = StateAttributeLimitsHelper(self, attribute='y_att',
                                                       lower='y_min', upper='y_max',
                                                       cache=self.limits_cache)

        self.z_lim_helper = StateAttributeLimitsHelper(self, attribute='z_att',
                                                       lower='z_min', upper='z_max',
                                                       cache=self.limits_cache)

        # TODO: if limits_cache is re-assigned to a different object, we need to
        # update the attribute helpers. However if in future we make limits_cache
        # into a smart dictionary that can call callbacks when elements are
        # changed then we shouldn't always call this. It'd also be nice to
        # avoid this altogether and make it more clean.
        self.add_callback('limits_cache', nonpartial(self._update_limits_cache))

    def _update_limits_cache(self):
        self.x_lim_helper._cache = self.limits_cache
        self.x_lim_helper._update_attribute()
        self.y_lim_helper._cache = self.limits_cache
        self.y_lim_helper._update_attribute()
        self.z_lim_helper._cache = self.limits_cache
        self.z_lim_helper._update_attribute()

    # @property
    # def aspect(self):
    #     # TODO: this could be cached based on the limits, but is not urgent
    #     aspect = np.array([1, 1, 1], dtype=float)
    #     if self.native_aspect:
    #         aspect[0] = 1.
    #         aspect[1] = (self.y_max - self.y_min) / (self.x_max - self.x_min)
    #         aspect[2] = (self.z_max - self.z_min) / (self.x_max - self.x_min)
    #         aspect /= aspect.max()
    #     return aspect

    # def reset(self):
    #     pass

    def flip_x(self):
        self.x_lim_helper.flip_limits()

    def flip_y(self):
        self.y_lim_helper.flip_limits()

    def flip_z(self):
        self.z_lim_helper.flip_limits()

    # @property
    # def clip_limits(self):
    #     return (self.x_min, self.x_max,
    #             self.y_min, self.y_max,
    #             self.z_min, self.z_max)

    # def set_limits(self, x_min, x_max, y_min, y_max, z_min, z_max):
    #     with delay_callback(self, 'x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max'):
    #         self.x_min = x_min
    #         self.x_max = x_max
    #         self.y_min = y_min
    #         self.y_max = y_max
    #         self.z_min = z_min
    #         self.z_max = z_max


class VolumeViewerState(ViewerState3D):

    def __init__(self, **kwargs):
        super(VolumeViewerState, self).__init__()
        self.add_callback('layers', self._update_attributes)
        self.update_from_dict(kwargs)

    def _update_attributes(self, *args):
        for layer_state in self.layers:
            if getattr(layer_state.layer, 'ndim', None) == 3:
                data = layer_state.layer
                break
        else:
            data = None

        if data is None:
            type(self).x_att.set_choices(self, [])
            type(self).y_att.set_choices(self, [])
            type(self).z_att.set_choices(self, [])

        else:
            z_cid, y_cid, x_cid = data.pixel_component_ids

            type(self).x_att.set_choices(self, [x_cid])
            type(self).y_att.set_choices(self, [y_cid])
            type(self).z_att.set_choices(self, [z_cid])


class Scatter3DViewerState(ViewerState3D):

    def __init__(self, **kwargs):

        super(Scatter3DViewerState, self).__init__()

        self.x_att_helper = ComponentIDComboHelper(self, 'x_att', categorical=True)
        self.y_att_helper = ComponentIDComboHelper(self, 'y_att', categorical=True)
        self.z_att_helper = ComponentIDComboHelper(self, 'z_att', categorical=True)

        self.add_callback('layers', self._on_layers_change)

        self.update_from_dict(kwargs)

    def _on_layers_change(self, *args):
        layers_data = [layer_state.layer for layer_state in self.layers]
        self.x_att_helper.set_multiple_data(layers_data)
        self.y_att_helper.set_multiple_data(layers_data)
        self.z_att_helper.set_multiple_data(layers_data)
