def test_non_hex_colors(app, data_volume):

    # Make sure non-hex colors such as '0.4' and 'red', which are valid
    # matplotlib colors, work as expected.

    viewer = app.volshow(data=data_volume)
    data_volume.style.color = '0.3'
    data_volume.style.color = 'indigo'

    app.subset('test', data_volume.main_components[0] > 1)
    viewer.layer_options.selected = 1
    data_volume.subsets[0].style.color = '0.5'
    data_volume.subsets[0].style.color = 'purple'
