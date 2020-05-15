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
    assert len(s.figure.marks) == 3
    s.remove_data(data_image)
    assert len(s.figure.marks) == 2
    s.remove_data(data_volume)
    assert len(s.figure.marks) == 1


def test_change_reference(app, data_image, data_volume):
    im = app.imshow(data=data_volume)
    im.add_data(data_image)
    im.state.reference_data = data_image
