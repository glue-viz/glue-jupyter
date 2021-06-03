def test_contour_levels(app, data_image):
    viewer = app.imshow(data=data_image)
    widget_state = viewer._layout_layer_options.layers[0]['layer_panel']
    layer_state = widget_state.layer_state
    layer_state.level_mode = "Custom"

    widget_state.c_levels_txt = '1e2, 1e3'
    assert layer_state.levels == [100, 1000]
    assert widget_state.c_levels_txt == '1e2, 1e3'

    layer_state.levels = [10, 100]
    assert widget_state.c_levels_txt == '10, 100'
