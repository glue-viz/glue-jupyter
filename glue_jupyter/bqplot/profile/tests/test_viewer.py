def test_non_hex_colors(app, dataxyz):

    # Make sure non-hex colors such as '0.4' and 'red', which are valid
    # matplotlib colors, work as expected.

    viewer = app.profile1d(data=dataxyz)
    dataxyz.style.color = '0.3'
    dataxyz.style.color = 'indigo'

    app.subset('test', dataxyz.id['x'] > 1)
    viewer.layer_options._layer_dropdown.value = viewer.layers[1]
    dataxyz.subsets[0].style.color = '0.5'
    dataxyz.subsets[0].style.color = 'purple'
