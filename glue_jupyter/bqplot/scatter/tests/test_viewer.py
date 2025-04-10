from itertools import permutations


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
