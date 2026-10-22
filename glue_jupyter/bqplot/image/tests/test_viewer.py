

from glue_jupyter.bqplot.image.frb_mark import FRBImage


def test_non_hex_colors(app, data_image):

    # Make sure non-hex colors such as '0.4' and 'red', which are valid
    # matplotlib colors, work as expected.

    viewer = app.imshow(data=data_image)
    data_image.style.color = '0.3'
    data_image.style.color = 'indigo'

    app.subset('test', data_image.main_components[0] > 1)
    viewer.layer_options.selected = 1
    data_image.subsets[0].style.color = '0.5'
    data_image.subsets[0].style.color = 'purple'


def test_remove(app, data_image, data_volume):
    s = app.imshow(data=data_image)
    s.add_data(data_volume)
    app.data_collection.new_subset_group(subset_state=data_image.id['intensity'] > 1, label='test')
    assert len(s.figure.marks) == 5  # 1 for composite, 2 for 2 subsets, 2 contours
    s.remove_data(data_image)
    assert len(s.figure.marks) == 3  # 1 composite, 1 contour, 1 subset
    s.remove_data(data_volume)
    assert len(s.figure.marks) == 1  # 1 composite


def test_change_reference(app, data_image, data_volume):
    im = app.imshow(data=data_volume)
    im.add_data(data_image)
    im.state.reference_data = data_image


def test_contour_levels(app, data_image, data_volume):
    s = app.imshow(data=data_image)
    layer = s.layers[0]
    assert layer.state.levels
    layer.state.c_min = 0
    layer.state.c_max = 10
    layer.state.n_levels = 3
    assert layer.state.levels == [0, 5, 10]
    # since we start invisible, we don't compute the contour lines
    assert len(layer.contour_artist.contour_lines) == 0
    # make the visible, so we trigger a compute
    layer.state.contour_visible = True
    assert len(layer.contour_artist.contour_lines) == 3
    layer.state.level_mode = 'Custom'
    layer.state.n_levels = 1
    assert layer.state.levels == [0, 5, 10]
    layer.state.level_mode = 'Linear'
    assert layer.state.levels == [0]
    assert len(layer.contour_artist.contour_lines) == 1

    # test the visual attributes
    layer.state.contour_visible = False
    assert layer.contour_artist.visible is False

    # since it's invisible, we should leave the contour lines alone
    layer.state.n_levels = 2
    assert len(layer.contour_artist.contour_lines) == 1
    # and update them again
    layer.state.contour_visible = True
    assert len(layer.contour_artist.contour_lines) == 2


def test_contour_state(app, data_image):
    s = app.imshow(data=data_image)
    layer = s.layers[0]
    layer.state.c_min = 0
    layer.state.c_max = 10
    layer.state.n_levels = 3
    layer.state.level_mode = 'Custom'
    layer.state.levels = [1, 2]
    assert layer.state.levels == [1, 2]
    layer.state.level_mode = 'Linear'
    # Without priority of levels, this gets set to [2, 3]
    assert layer.state.levels == [0, 5, 10]


def test_add_markers_zoom(app, data_image, data_volume, dataxyz):

    # Regression test for a bug that caused the zoom to be
    # reset when adding markers to an image

    im = app.imshow(data=data_image)

    im.state.x_min = 0.2
    im.state.x_max = 0.4
    im.state.y_min = 0.3
    im.state.y_max = 0.5

    app.add_link(data_image, data_image.pixel_component_ids[0], dataxyz, dataxyz.id['y'])
    app.add_link(data_image, data_image.pixel_component_ids[1], dataxyz, dataxyz.id['x'])
    im.add_data(dataxyz)

    assert im.state.x_min == 0.2
    assert im.state.x_max == 0.4
    assert im.state.y_min == 0.3
    assert im.state.y_max == 0.5

    im.add_data(data_volume)

    assert im.state.x_min == 0.2
    assert im.state.x_max == 0.4
    assert im.state.y_min == 0.3
    assert im.state.y_max == 0.5

    im.state.reference_data = data_volume

    assert im.state.x_min == -0.5
    assert im.state.x_max == 63.5
    assert im.state.y_min == -0.5
    assert im.state.y_max == 63.5


def test_snap_to_lattice():

    # The FRB sampling grid is snapped to a power-of-two lattice aligned with
    # the data pixel grid so that nearest-neighbour sampling stays stable under
    # panning and zooming (otherwise a noisy background flickers).

    snap = FRBImage._snap_to_lattice

    # A heavily decimated view (8000 data pixels across 800 display samples)
    # snaps to a step of 8 - the largest power of two no coarser than the
    # display sampling of ~10 data pixels per sample.
    lo, hi, n = snap(1000.0, 9000.0, 800)
    assert lo == 1000.0 and hi == 9000.0
    assert (hi - lo) / (n - 1) == 8.0

    # Panning by less than one lattice step does not move the leading sample
    # off its data pixels: the lower bound and step are unchanged, so the
    # already-sampled pixels are identical (only the trailing edge can grow).
    lo2, hi2, n2 = snap(1000.3, 9000.3, 800)
    assert lo2 == 1000.0
    assert (hi2 - lo2) / (n2 - 1) == 8.0

    # Zooming changes the resolution only in factors of two, and each coarser
    # lattice is a subset of the finer one (its bounds lie on the finer grid).
    _, _, _ = snap(1000.0, 9000.0, 800)
    coarse_lo, coarse_hi, coarse_n = snap(1000.0, 9000.0, 800)
    fine_lo, fine_hi, fine_n = snap(1000.0, 5000.0, 800)
    coarse_step = (coarse_hi - coarse_lo) / (coarse_n - 1)
    fine_step = (fine_hi - fine_lo) / (fine_n - 1)
    assert coarse_step == 2 * fine_step
    assert coarse_lo % fine_step == 0 and coarse_hi % fine_step == 0

    # When zoomed in past 1:1 we never sample finer than the data grid.
    lo3, hi3, n3 = snap(100.0, 300.0, 800)
    assert (hi3 - lo3) / (n3 - 1) == 1.0
