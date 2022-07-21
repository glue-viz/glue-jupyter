import glue_jupyter.state_traitlets_helpers


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
    assert layer.state.levels == [2.5, 5, 7.5]
    # since we start invisible, we don't compute the contour lines
    assert len(layer.contour_artist.contour_lines) == 0
    # make the visible, so we trigger a compute
    layer.state.contour_visible = True
    assert len(layer.contour_artist.contour_lines) == 3
    layer.state.level_mode = 'Custom'
    layer.state.n_levels = 1
    assert layer.state.levels == [2.5, 5, 7.5]
    layer.state.level_mode = 'Linear'
    assert layer.state.levels == [5]
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
    glue_jupyter.state_traitlets_helpers.update_state_from_dict(
        layer.state,
        {'level_mode': 'Custom', 'levels': [1, 2]}
    )
    assert layer.state.levels == [1, 2]
    glue_jupyter.state_traitlets_helpers.update_state_from_dict(
        layer.state,
        {'level_mode': 'Linear', 'levels': [2, 3]}
    )
    # Without priority of levels, this gets set to [2, 3]
    assert layer.state.levels == [2.5, 5, 7.5]


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
