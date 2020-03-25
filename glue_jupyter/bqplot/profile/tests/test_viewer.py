def test_non_hex_colors(app, dataxyz):

    # Make sure non-hex colors such as '0.4' and 'red', which are valid
    # matplotlib colors, work as expected.

    viewer = app.profile1d(data=dataxyz)
    dataxyz.style.color = '0.3'
    dataxyz.style.color = 'indigo'

    app.subset('test', dataxyz.id['x'] > 1)
    viewer.layer_options.selected = 1
    dataxyz.subsets[0].style.color = '0.5'
    dataxyz.subsets[0].style.color = 'purple'


def test_remove(app, data_image, data_volume):
    s = app.profile1d(data=data_image)
    s.add_data(data_volume)
    app.data_collection.new_subset_group(subset_state=data_image.id['intensity'] > 1, label='test')
    assert len(s.figure.marks) == 4
    s.remove_data(data_image)
    assert len(s.figure.marks) == 2
    s.remove_data(data_volume)
    assert len(s.figure.marks) == 0
