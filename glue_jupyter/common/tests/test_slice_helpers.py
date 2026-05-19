from itertools import permutations
from random import sample

from ipyvuetify import Slider

from ..slice_helpers import MultiSliceWidgetHelper

from echo import CallbackProperty, HasCallbackProperties


class ViewerTestState2D(HasCallbackProperties):
    x_att = CallbackProperty()
    y_att = CallbackProperty()
    reference_data = CallbackProperty()
    slices = CallbackProperty()


class ViewerTestState3D(ViewerTestState2D):
    z_att = CallbackProperty()


def test_2d_sliders_3d(data_volume):
    state = ViewerTestState2D()
    state.reference_data = data_volume
    state.slices = (0,) * data_volume.ndim

    helper = MultiSliceWidgetHelper(viewer_state=state)
    for perm in permutations(range(data_volume.ndim)):
        state.x_att = data_volume.pixel_component_ids[perm[0]]
        state.y_att = data_volume.pixel_component_ids[perm[1]]
        assert isinstance(helper._sliders[perm[2]], Slider)
        assert all(slider is None
                   for index, slider in enumerate(helper._sliders)
                   if index != perm[2])


def test_3d_sliders_3d(data_volume):
    state = ViewerTestState3D()
    state.reference_data = data_volume
    state.slices = (0,) * data_volume.ndim

    helper = MultiSliceWidgetHelper(viewer_state=state)
    for perm in permutations(range(data_volume.ndim)):
        state.x_att = data_volume.pixel_component_ids[perm[0]]
        state.y_att = data_volume.pixel_component_ids[perm[1]]
        state.z_att = data_volume.pixel_component_ids[perm[2]]
        assert all(slider is None for slider in helper._sliders)


def test_3d_sliders_4d(data_4d):
    state = ViewerTestState3D()
    state.reference_data = data_4d
    state.slices = (0,) * data_4d.ndim

    helper = MultiSliceWidgetHelper(viewer_state=state)
    for perm in permutations(range(data_4d.ndim)):
        state.x_att = data_4d.pixel_component_ids[perm[0]]
        state.y_att = data_4d.pixel_component_ids[perm[1]]
        state.z_att = data_4d.pixel_component_ids[perm[2]]
        assert isinstance(helper._sliders[perm[3]], Slider)
        assert all(slider is None
                   for index, slider in enumerate(helper._sliders)
                   if index != perm[3])


def test_no_slider_if_flat(data_flat):
    # The "flat" (length 1) dimension is along axis 2
    state = ViewerTestState3D()
    state.reference_data = data_flat
    state.x_att = data_flat.pixel_component_ids[0]
    state.y_att = data_flat.pixel_component_ids[1]
    state.z_att = data_flat.pixel_component_ids[3]
    state.slices = (0,) * data_flat.ndim

    helper = MultiSliceWidgetHelper(viewer_state=state)
    assert helper._sliders[2] is None


def test_slider_slice_values(data_4d):
    state = ViewerTestState3D()
    state.reference_data = data_4d
    state.x_att = data_4d.pixel_component_ids[0]
    state.y_att = data_4d.pixel_component_ids[1]
    state.z_att = data_4d.pixel_component_ids[2]
    state.slices = (0,) * data_4d.ndim

    helper = MultiSliceWidgetHelper(viewer_state=state)
    size3 = data_4d.shape[3]
    index_values = list(range(size3))
    permutation = sample(index_values, len(index_values))
    for idx in permutation:
        helper._sliders[3].value = idx
        assert state.slices[3] == idx

    for idx in permutation:
        state.slices = tuple(slice if index != 3 else idx
                             for index, slice
                             in enumerate(state.slices))
        assert helper._sliders[3].value == idx
