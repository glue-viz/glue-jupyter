from itertools import permutations

from numpy.testing import assert_allclose, assert_equal

from glue.core import Data
from glue.core.roi import RectangularROI
from glue.core.link_helpers import LinkSame, LinkSameWithUnits


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
    assert len(s.figure.marks) == 24
    s.remove_data(dataxyz)
    assert len(s.figure.marks) == 12
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


def test_unit_conversion(app):

    d1 = Data(a=[1, 2, 3], b=[2, 3, 4])
    d1.get_component('a').units = 'm'
    d1.get_component('b').units = 's'

    d2 = Data(c=[2000, 1000, 3000], d=[0.001, 0.002, 0.004])
    d2.get_component('c').units = 'mm'
    d2.get_component('d').units = 'ks'

    # d3 is the same as d2 but we will link it differently
    d3 = Data(e=[2000, 1000, 3000], f=[0.001, 0.002, 0.004])
    d3.get_component('e').units = 'mm'
    d3.get_component('f').units = 'ks'

    d4 = Data(g=[2, 2, 3], h=[1, 2, 1])
    d4.get_component('g').units = 'kg'
    d4.get_component('h').units = 'm/s'

    session = app.session

    data_collection = session.data_collection
    data_collection.append(d1)
    data_collection.append(d2)
    data_collection.append(d3)
    data_collection.append(d4)

    data_collection.add_link(LinkSameWithUnits(d1.id['a'], d2.id['c']))
    data_collection.add_link(LinkSameWithUnits(d1.id['b'], d2.id['d']))
    data_collection.add_link(LinkSame(d1.id['a'], d3.id['e']))
    data_collection.add_link(LinkSame(d1.id['b'], d3.id['f']))
    data_collection.add_link(LinkSame(d1.id['a'], d4.id['g']))
    data_collection.add_link(LinkSame(d1.id['b'], d4.id['h']))

    viewer = app.scatter2d(data=d1)
    viewer.add_data(d2)
    viewer.add_data(d3)
    viewer.add_data(d4)

    assert viewer.layers[0].enabled
    assert viewer.layers[1].enabled
    assert viewer.layers[2].enabled
    assert viewer.layers[3].enabled

    assert viewer.state.x_axislabel == 'a [m]'
    assert viewer.state.y_axislabel == 'b [s]'

    assert_allclose(viewer.layers[0].scatter_mark.x, [1, 2, 3])
    assert_allclose(viewer.layers[0].scatter_mark.y, [2, 3, 4])
    assert_allclose(viewer.layers[1].scatter_mark.x, [2, 1, 3])
    assert_allclose(viewer.layers[1].scatter_mark.y, [1, 2, 4])
    assert_allclose(viewer.layers[2].scatter_mark.x, [2000, 1000, 3000])
    assert_allclose(viewer.layers[2].scatter_mark.y, [0.001, 0.002, 0.004])
    assert_allclose(viewer.layers[3].scatter_mark.x, [2, 2, 3])
    assert_allclose(viewer.layers[3].scatter_mark.y, [1, 2, 1])

    assert viewer.state.x_min == 0.92
    assert viewer.state.x_max == 3.08
    assert viewer.state.y_min == 1.92
    assert viewer.state.y_max == 4.08

    roi = RectangularROI(0.5, 2.5, 1.5, 4.5)
    viewer.apply_roi(roi)

    assert len(d1.subsets) == 1
    assert_equal(d1.subsets[0].to_mask(), [1, 1, 0])

    # Because of the LinkSameWithUnits, the points actually appear in the right
    # place even before we set the display units.
    assert len(d2.subsets) == 1
    assert_equal(d2.subsets[0].to_mask(), [0, 1, 0])

    # d3 is only linked with LinkSame not LinkSameWithUnits so currently the
    # points are outside the visible axes
    assert len(d3.subsets) == 1
    assert_equal(d3.subsets[0].to_mask(), [0, 0, 0])

    # As we haven't set display units yet, the values for this dataset are shown
    # on the same scale as for d1 as if the units had never been set.
    assert len(d4.subsets) == 1
    assert_equal(d4.subsets[0].to_mask(), [0, 1, 0])

    # Now try setting the units explicitly

    viewer.state.x_display_unit = 'km'
    viewer.state.y_display_unit = 'ms'

    assert viewer.state.x_axislabel == 'a [km]'
    assert viewer.state.y_axislabel == 'b [ms]'

    assert_allclose(viewer.layers[0].scatter_mark.x, [1e-3, 2e-3, 3e-3])
    assert_allclose(viewer.layers[0].scatter_mark.y, [2e3, 3e3, 4e3])
    assert_allclose(viewer.layers[1].scatter_mark.x, [2e-3, 1e-3, 3e-3])
    assert_allclose(viewer.layers[1].scatter_mark.y, [1e3, 2e3, 4e3])
    assert_allclose(viewer.layers[2].scatter_mark.x, [2, 1, 3])
    assert_allclose(viewer.layers[2].scatter_mark.y, [1, 2, 4])
    assert_allclose(viewer.layers[3].scatter_mark.x, [2e-3, 2e-3, 3e-3])
    assert_allclose(viewer.layers[3].scatter_mark.y, [1e3, 2e3, 1e3])

    assert_allclose(viewer.state.x_min, 0.92e-3)
    assert_allclose(viewer.state.x_max, 3.08e-3)
    assert_allclose(viewer.state.y_min, 1.92e3)
    assert_allclose(viewer.state.y_max, 4.08e3)

    roi = RectangularROI(0.5e-3, 2.5e-3, 1.5e3, 4.5e3)
    viewer.apply_roi(roi)

    # Results are as above - the display units do not result in any changes to
    # the actual content of the axes and does not deal with automatic conversion
    # of different units between different datasets - LinkSameWithUnits should
    # deal with that already.

    assert_equal(d1.subsets[0].to_mask(), [1, 1, 0])
    assert_equal(d2.subsets[0].to_mask(), [0, 1, 0])
    assert_equal(d3.subsets[0].to_mask(), [0, 0, 0])
    assert_equal(d4.subsets[0].to_mask(), [0, 1, 0])

    # Change the limits to make sure they are always converted
    viewer.state.x_min = 0.0001
    viewer.state.x_max = 0.005
    viewer.state.y_min = 200
    viewer.state.y_max = 7000

    viewer.state.x_display_unit = 'm'
    viewer.state.y_display_unit = 's'
#
    assert viewer.state.x_axislabel == 'a [m]'
    assert viewer.state.y_axislabel == 'b [s]'

    assert_allclose(viewer.layers[0].scatter_mark.x, [1, 2, 3])
    assert_allclose(viewer.layers[0].scatter_mark.y, [2, 3, 4])
    assert_allclose(viewer.layers[1].scatter_mark.x, [2, 1, 3])
    assert_allclose(viewer.layers[1].scatter_mark.y, [1, 2, 4])
    assert_allclose(viewer.layers[2].scatter_mark.x, [2000, 1000, 3000])
    assert_allclose(viewer.layers[2].scatter_mark.y, [0.001, 0.002, 0.004])
    assert_allclose(viewer.layers[3].scatter_mark.x, [2, 2, 3])
    assert_allclose(viewer.layers[3].scatter_mark.y, [1, 2, 1])

    assert viewer.state.x_min == 0.1
    assert viewer.state.x_max == 5
    assert viewer.state.y_min == 0.2
    assert viewer.state.y_max == 7
