from itertools import permutations, product
from glue.core.subset import SubsetState


def test_non_hex_colors(app, dataxyz):

    # Make sure non-hex colors such as '0.4' and 'red', which are valid
    # matplotlib colors, work as expected.

    viewer = app.histogram1d(data=dataxyz)
    dataxyz.style.color = '0.3'
    dataxyz.style.color = 'indigo'

    app.subset('test', dataxyz.id['x'] > 1)
    viewer.layer_options.selected = 1
    dataxyz.subsets[0].style.color = '0.5'
    dataxyz.subsets[0].style.color = 'purple'


def test_remove_from_viewer(app, dataxz, dataxyz):
    s = app.histogram1d(data=dataxyz)
    s.add_data(dataxz)
    app.data_collection.new_subset_group(subset_state=dataxz.id['x'] > 1, label='test')
    assert len(s.figure.marks) == 4
    s.remove_data(dataxyz)
    assert len(s.figure.marks) == 2
    s.remove_data(dataxz)
    assert len(s.figure.marks) == 0


def test_remove_from_data_collection(app, dataxz, dataxyz):
    s = app.histogram1d(data=dataxyz)
    s.add_data(dataxz)
    app.data_collection.new_subset_group(subset_state=dataxz.id['x'] > 1, label='test')
    assert len(s.figure.marks) == 4
    s.state.hist_n_bin = 30
    app.data_collection.remove(dataxyz)
    assert len(s.figure.marks) == 2
    s.state.hist_n_bin = 20
    app.data_collection.remove(dataxz)
    assert len(s.figure.marks) == 0
    s.state.hist_n_bin = 10


def test_redraw_empty_subset(app, dataxz):
    s = app.histogram1d(data=dataxz)
    s.add_data(dataxz)
    app.data_collection.new_subset_group(subset_state=dataxz.id['x'] > 1, label='empty_test')
    layer_artist = s.layers[-1]
    subset = layer_artist.layer
    subset.subset_state = SubsetState()

    # Test each combination of cumulative, normalize, and y_log
    for flags in product([True, False], repeat=3):
        s.state.cumulative, s.state.normalize, s.state.y_log = flags
        assert all(layer_artist.bars.y == 0)


def test_zorder(app, data_volume, dataxz, dataxyz):
    s = app.histogram1d(data=dataxyz)
    s.add_data(dataxz)
    s.add_data(data_volume)
    xyz, xz, vol = s.layers

    for p in permutations([1, 2, 3]):
        vol.state.zorder, xz.state.zorder, xyz.state.zorder = p
        it = iter(s.figure.marks)
        assert all(layer.bars in it for layer in s.layers)
