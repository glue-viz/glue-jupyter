def test_contour_levels(app, data_image):
    viewer = app.imshow(data=data_image)
    widget_state = viewer._layout_layer_options.layers[0]['layer_panel']
    layer_state = widget_state.layer_state
    layer_state.level_mode = "Custom"

    widget_state.c_levels_txt = '1e2, 1e3, 0.1, .1'
    assert layer_state.levels == [100, 1000, 0.1, 0.1]
    assert widget_state.c_levels_txt == '1e2, 1e3, 0.1, .1'

    layer_state.levels = [10, 100]
    assert widget_state.c_levels_txt == '10, 100'


def test_no_slider_if_flat(app, data_flat):
    viewer = app.imshow(data=data_flat)
    widget = viewer.viewer_options

    viewer.state.reference_data = data_flat
    viewer.state.x_att = data_flat.pixel_component_ids[0]
    viewer.state.y_att = data_flat.pixel_component_ids[1]

    assert len(widget.sliders) == 1
    assert {slider['index'] for slider in widget.sliders} == {3}

    viewer.state.x_att = data_flat.pixel_component_ids[2]

    assert len(widget.sliders) == 2
    assert {slider['index'] for slider in widget.sliders} == {0, 3}
