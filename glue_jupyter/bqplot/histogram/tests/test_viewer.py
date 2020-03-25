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


def test_remove(app, dataxz, dataxyz):
    s = app.histogram1d(data=dataxyz)
    s.add_data(dataxz)
    app.data_collection.new_subset_group(subset_state=dataxz.id['x'] > 1, label='test')
    assert len(s.figure.marks) == 4
    s.remove_data(dataxyz)
    assert len(s.figure.marks) == 2
    s.remove_data(dataxz)
    assert len(s.figure.marks) == 0
