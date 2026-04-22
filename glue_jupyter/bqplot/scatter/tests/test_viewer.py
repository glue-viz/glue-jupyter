from itertools import permutations

import pytest

from bqplot_linlog import LinLogScale


def test_scatter2d_log(app, dataxyz):

    s = app.scatter2d(data=dataxyz)

    # Initially linear scales
    assert isinstance(s.scale_x, LinLogScale)
    assert s.scale_x.mode == 'linear'
    assert s.scale_y.mode == 'linear'

    # Switch x to log
    s.state.x_log = True
    assert s.scale_x.mode == 'log'
    assert s.scale_y.mode == 'linear'

    # The same scale object is reused (no replacement needed)
    original_scale_x = s.scale_x
    s.state.x_log = False
    assert s.scale_x is original_scale_x
    assert s.scale_x.mode == 'linear'

    # Switch y to log
    s.state.y_log = True
    assert s.scale_y.mode == 'log'

    # Switch back to linear
    s.state.y_log = False
    assert s.scale_y.mode == 'linear'


def test_scatter2d_log_limits(app):

    # Regression test: when toggling log scale with limits that include
    # negative values, the limits should be automatically reset to
    # positive values by the state's limit helper.

    d = app.add_data(data={'x': [-10, -5, 0, 5, 15, 30],
                           'y': [-5, 10, 20, 35, 40, 50]})[0]
    s = app.scatter2d(data=d)

    assert s.state.x_min < 0

    s.state.x_log = True
    assert s.state.x_min > 0
    assert s.state.x_max > 0
    assert s.scale_x.min == s.state.x_min
    assert s.scale_x.max == s.state.x_max

    # Also test the case where the user pans to negative limits
    # with all-positive data, then enables log
    s.state.x_log = False
    s.state.x_min = -10
    s.state.x_max = 30

    s.state.x_log = True
    assert s.state.x_min > 0
    assert s.scale_x.min == s.state.x_min
    assert s.scale_x.max == s.state.x_max


@pytest.mark.parametrize('n_toggles', [3, 5, 7])
def test_scatter2d_log_repeated_toggle(app, dataxyz, n_toggles):
    # Regression test: toggling log scale back and forth multiple times
    # should always leave the viewer in a consistent state.
    # With LinLogScale, the scale object is never replaced, so this
    # is mainly checking that the mode stays in sync.

    s = app.scatter2d(data=dataxyz)
    original_scale_x = s.scale_x
    original_scale_y = s.scale_y

    for i in range(n_toggles):
        s.state.x_log = not s.state.x_log
        s.state.y_log = not s.state.y_log

        expected_x = 'log' if s.state.x_log else 'linear'
        expected_y = 'log' if s.state.y_log else 'linear'

        # Scale object is always the same
        assert s.scale_x is original_scale_x, f"x scale replaced after toggle {i+1}"
        assert s.scale_y is original_scale_y, f"y scale replaced after toggle {i+1}"

        # Mode matches the state
        assert s.scale_x.mode == expected_x, f"x scale mode wrong after toggle {i+1}"
        assert s.scale_y.mode == expected_y, f"y scale mode wrong after toggle {i+1}"

        # Limits are synced between state and scale
        if s.state.x_min is not None and s.state.x_max is not None:
            assert s.scale_x.min == float(s.state.x_min), \
                f"x_min out of sync after toggle {i+1}"
            assert s.scale_x.max == float(s.state.x_max), \
                f"x_max out of sync after toggle {i+1}"
        if s.state.y_min is not None and s.state.y_max is not None:
            assert s.scale_y.min == float(s.state.y_min), \
                f"y_min out of sync after toggle {i+1}"
            assert s.scale_y.max == float(s.state.y_max), \
                f"y_max out of sync after toggle {i+1}"


def test_scatter2d_nd(app, data_4d):
    # Regression test for a bug that meant that arrays with more than one
    # dimension did not work correctly.
    app.add_data(data_4d)
    scatter = app.scatter2d(x='x', y='x', data=data_4d)
    scatter.state.layers[0].vector_visible = True
    scatter.state.layers[0].size_mode = 'Linear'
    scatter.state.layers[0].cmap_mode = 'Linear'


def test_scatter2d_categorical(app, datacat):
    # Make sure that things work correctly with arrays that have categorical
    # components - we use the numerical codes for these. In future we should
    # make sure that we show the correct labels on the axes.
    app.add_data(datacat)
    scatter = app.scatter2d(data=datacat)
    scatter.state.layers[0].vector_visible = True
    scatter.state.layers[0].size_mode = 'Linear'
    scatter.state.layers[0].cmap_mode = 'Linear'
    assert str(scatter.state.x_att) == 'a'
    assert str(scatter.state.y_att) == 'b'


def test_non_hex_colors(app, dataxyz):

    # Make sure non-hex colors such as '0.4' and 'red', which are valid
    # matplotlib colors, work as expected.

    viewer = app.scatter2d(data=dataxyz)
    dataxyz.style.color = '0.3'
    dataxyz.style.color = 'indigo'

    app.subset('test', dataxyz.id['x'] > 1)
    viewer.layer_options.selected = 1
    dataxyz.subsets[0].style.color = '0.5'
    dataxyz.subsets[0].style.color = 'purple'


def test_remove(app, dataxz, dataxyz):
    s = app.scatter2d(data=dataxyz)
    s.add_data(dataxz)
    app.data_collection.new_subset_group(subset_state=dataxz.id['x'] > 1, label='test')
    assert len(s.figure.marks) == 16
    s.remove_data(dataxyz)
    assert len(s.figure.marks) == 8
    s.remove_data(dataxz)
    assert len(s.figure.marks) == 0


def test_zorder(app, data_volume, dataxz, dataxyz):
    s = app.scatter2d(data=dataxyz)
    s.add_data(dataxz)
    s.add_data(data_volume)
    xyz, xz, vol = s.layers

    for p in permutations([1, 2, 3]):
        vol.state.zorder, xz.state.zorder, xyz.state.zorder = p
        it = iter(s.figure.marks)
        assert all(layer.scatter_mark in it for layer in s.layers)


def test_limits_init(app, dataxz, dataxyz):

    # Regression test for a bug that caused the bqplot limits
    # to not match the glue state straight after initialization

    s = app.scatter2d(data=dataxyz)

    assert s.state.x_min == 0.92
    assert s.state.x_max == 3.08
    assert s.state.y_min == 1.92
    assert s.state.y_max == 4.08

    assert s.scale_x.min == 0.92
    assert s.scale_x.max == 3.08
    assert s.scale_y.min == 1.92
    assert s.scale_y.max == 4.08


def test_incompatible_data(app):

    # Regression test for a bug that caused the scatter viewer to raise an
    # exception if an incompatible dataset was present, and also for a bug
    # that occurred when trying to remove the original dataset

    d1 = app.add_data(data={'x': [1, 2, 3], 'y': [1, 2, 1]})[0]
    d2 = app.add_data(data={'x': [2, 3, 4], 'y': [2, 3, 2]})[0]

    s = app.scatter2d(data=d1)
    s.add_data(d2)

    assert s.state.x_att is d1.id['x']
    assert s.state.y_att is d1.id['y']

    assert len(s.layers) == 2
    assert s.layers[0].enabled
    assert not s.layers[1].enabled

    app.data_collection.remove(d1)

    assert s.state.x_att is d2.id['x']
    assert s.state.y_att is d2.id['y']

    assert len(s.layers) == 1
    assert s.layers[0].enabled
