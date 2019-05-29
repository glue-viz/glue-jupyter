def test_non_hex_colors(app, data_image):

    # Make sure non-hex colors such as '0.4' and 'red', which are valid
    # matplotlib colors, work as expected.

    viewer = app.imshow(data=data_image)
    data_image.style.color = '0.3'
    data_image.style.color = 'indigo'

    app.subset('test', data_image.main_components[0] > 1)
    viewer.layer_options._layer_dropdown.value = viewer.layers[1]
    data_image.subsets[0].style.color = '0.5'
    data_image.subsets[0].style.color = 'purple'
