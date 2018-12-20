def test_histogram1d(app, dataxyz):
    s = app.histogram1d('y', data=dataxyz)
    assert s.state.x_att == 'y'
    assert len(s.layers) == 1
    assert s.layers[0].layer['y'].tolist() == [2, 3, 4]
    print('updating histogram state')
    s.state.hist_x_min = 1.5
    s.state.hist_x_max = 4.5
    s.state.hist_n_bin = 3
    assert s.layers[0].bins.tolist() == [1.5, 2.5, 3.5, 4.5]
    assert s.layers[0].hist.tolist() == [1, 1, 1]

    app.subset('test', dataxyz.id['x'] > 1)
    assert len(s.layers) == 2
    assert s.layers[1].layer['y'].tolist() == [3, 4]
    assert s.layers[1].bins.tolist() == [1.5, 2.5, 3.5, 4.5]
    assert s.layers[1].hist.tolist() == [0, 1, 1]

    s.interact_brush_x.brushing = True
    s.interact_brush_x.selected = [2.5, 3.5]
    s.interact_brush_x.brushing = False

    assert len(s.layers) == 3
    assert s.layers[2].bins.tolist() == [1.5, 2.5, 3.5, 4.5]
    assert s.layers[2].hist.tolist() == [0, 1, 0]

    # s.state.hist_n_bin = 6
    # assert s.layers[2].bins.tolist() == [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
    # assert s.layers[2].hist.tolist() == [0, 1, 0, 0, 0, 0]


def test_interact(app, dataxyz):
    s = app.scatter2d('x', 'y', data=dataxyz)
    # s.widget_menu_select_x.value = True
    # s.widget_menu_select_x.click()# = True
    s.widget_button_interact.value = s.interact_brush_x
    assert s.figure.interaction == s.interact_brush_x


def test_scatter2d(app, dataxyz, dataxz):
    s = app.scatter2d('x', 'y', data=dataxyz)
    assert s.state.x_att == 'x'
    assert s.state.y_att == 'y'

    # assert s.state.x_min == 1
    # assert s.state.x_max == 3
    # assert s.state.y_min == 2
    # assert s.state.y_max == 4

    # test when we swap x and x
    s = app.scatter2d('y', 'x', data=dataxyz)
    assert s.state.x_att == 'y'
    assert s.state.y_att == 'x'
    # assert s.state.y_min == 1
    # assert s.state.y_max == 3
    # assert s.state.x_min == 2
    # assert s.state.x_max == 4

    s.layers[0].state.size_mode = 'Linear'

    layer = s.layers[0]
    assert not layer.quiver.visible
    layer.state.vector_visible = True
    assert layer.quiver.visible


def test_scatter2d_density(app, dataxyz):
    s = app.scatter2d('x', 'y', data=dataxyz)
    s.layers[0].state.points_mode = 'density'
    assert s.layers[0].state.density_map == True

    s.state.x_min == 1
    s.state.x_max == 3
    s.state.y_min == 2
    s.state.y_max == 4
    assert s.layers[0].state.density_map == True
    s.layers[0].state.bins = 2
    assert s.layers[0].image.image.tolist() == [[0, 1], [0, 0]]


def test_scatter2d_subset(app, dataxyz, dataxz):
    s = app.scatter2d('x', 'y', data=dataxyz)
    app.subset('test', dataxyz.id['x'] > 2)
    assert len(s.layers) == 2
    assert s.layers[1].layer['x'].tolist() == [3]
    assert s.layers[1].layer['y'].tolist() == [4]
    assert s.layers[1].layer['z'].tolist() == [7]

    assert s.layers[1].scatter.x.tolist() == [1, 2, 3]
    assert s.layers[1].scatter.y.tolist() == [2, 3, 4]
    assert s.layers[1].scatter.selected == [2]

    s.state.y_att = 'z'
    assert s.layers[1].scatter.x.tolist() == [1, 2, 3]
    assert s.layers[1].scatter.y.tolist() == [5, 6, 7]
    assert s.layers[1].scatter.selected == [2]


def test_scatter2d_brush(app, dataxyz, dataxz):
    s = app.scatter2d('x', 'y', data=dataxyz)

    # 1d x brushing
    #s.button_action.value = 'brush x'
    s.interact_brush_x.brushing = True
    s.interact_brush_x.selected = [1.5, 3.5]
    s.interact_brush_x.brushing = False
    assert len(s.layers) == 2
    assert s.layers[1].layer['x'].tolist() == [2, 3]
    assert s.layers[1].layer['y'].tolist() == [3, 4]
    assert s.layers[1].layer['z'].tolist() == [6, 7]

    assert s.layers[1].scatter.x.tolist() == [1, 2, 3]
    assert s.layers[1].scatter.y.tolist() == [2, 3, 4]
    assert s.layers[1].scatter.selected.tolist() == [1, 2]

    # 1d y brushing is not working for bqplot
    # s.button_action.value = 'brush y'
    # s.brush_y.brushing = True
    # s.brush_y.selected = [1.5, 3.5]
    # s.brush_y.brushing = False
    # assert len(s.layers) == 2
    # assert s.layers[1].layer['x'].tolist() == [1, 2]
    # assert s.layers[1].layer['y'].tolist() == [2, 3]
    # assert s.layers[1].layer['z'].tolist() == [5, 6]

    # assert s.layers[1].scatter.x.tolist() == [1, 2, 3]
    # assert s.layers[1].scatter.y.tolist() == [2, 3, 4]
    # assert s.layers[1].scatter.selected == [0, 1]

    # 2d brushing
    # format is (x1, y1), (x2, y2)
    s.interact_brush.brushing = True
    s.interact_brush.selected = [(1.5, 3.5), (3.5, 5)]
    s.interact_brush.brushing = False
    assert len(s.layers) == 2
    assert s.layers[1].layer['x'].tolist() == [3]
    assert s.layers[1].layer['y'].tolist() == [4]
    assert s.layers[1].layer['z'].tolist() == [7]

    assert s.layers[1].scatter.x.tolist() == [1, 2, 3]
    assert s.layers[1].scatter.y.tolist() == [2, 3, 4]
    assert s.layers[1].scatter.selected == [2]

    # nothing should change when we change modes
    s.widget_button_interact.value = s.interact_brush_x
    assert s.layers[1].scatter.selected == [2]
    s.widget_button_interact.value = s.interact_brush_y
    assert s.layers[1].scatter.selected == [2]


def test_scatter2d_properties(app, dataxyz, dataxz):
    s = app.scatter2d('x', 'y', data=dataxyz)
    l1 = s.layers[0]
    l1.state.color = 'green'
    assert l1.scatter.colors == ['green']
    l1.scatter.colors = ['orange']
    assert l1.state.color == 'orange'


def test_scatter2d_cmap_mode(app, dataxyz):
    s = app.scatter2d('x', 'y', data=dataxyz)
    l1 = s.layers[0]
    assert l1.state.cmap_mode == 'Fixed', 'expected default value'
    assert l1.state.cmap_name == 'Gray'

    assert l1.scatter.color is None
    l1.state.cmap_att = 'x'
    l1.state.cmap_mode = 'Linear'
    assert l1.widget_color.widget_cmap_mode.label == 'Linear'
    assert l1.state.cmap_name == 'Gray'
    l1.state.cmap_vmin = 0
    l1.state.cmap_vmax = 10
    assert l1.scatter.color is not None

    l1.widget_color.widget_cmap.label = 'Viridis'
    assert l1.state.cmap_name == 'Viridis'
    assert l1.widget_color.widget_cmap.label == 'Viridis'

    l1.widget_color.widget_cmap.label = 'Gray'
    assert l1.widget_color.widget_cmap.label == 'Gray'
    assert l1.state.cmap_name == 'Gray'


def test_scatter2d_and_histogram(app, dataxyz):
    s = app.scatter2d('x', 'y', data=dataxyz)
    h = app.histogram1d('x', data=dataxyz)
    s.interact_brush.brushing = True
    s.interact_brush.selected = [(1.5, 3.5), (3.5, 5)]
    s.interact_brush.brushing = False
    assert len(s.layers) == 2
    import glue.core.subset
    assert isinstance(s.layers[1].layer.subset_state,
                      glue.core.subset.RoiSubsetState)


def test_imshow(app, data_image, dataxyz):
    assert data_image in app.data_collection
    v = app.imshow(data=data_image)

    v.add_data(dataxyz)

    assert len(v.layers) == 2
    v.interact_brush.brushing = True
    v.interact_brush.selected = [(1.5, 3.5), (300.5, 550)]
    v.interact_brush.brushing = False

    assert len(v.layers) == 4

    v.layers[0].state.cmap = 'Grey'
    assert v.layers[0].widget_colormap.label == 'Grey'
    assert isinstance(v.layers[0].widget_colormap.value, list)
    assert v.layers[0].scale_image.scheme

    v.layers[0].state.cmap = 'Jet'
    assert v.layers[0].widget_colormap.label == 'Jet'
    assert v.layers[0].widget_colormap.value == 'jet'
    assert v.layers[0].scale_image.scheme == 'jet'
    assert v.layers[0].scale_image.colors == []


def test_imshow_equal_aspect(app, data_image):
    assert data_image in app.data_collection
    v = app.imshow(data=data_image)
    assert v.widgets_aspect.value
    assert v.figure.min_aspect_ratio == 1
    assert v.figure.max_aspect_ratio == 1
    v.state.aspect = 'auto'
    assert not v.widgets_aspect.value
    assert v.figure.min_aspect_ratio == 0.01
    assert v.figure.max_aspect_ratio == 100
    v.state.aspect = 'equal'
    assert v.widgets_aspect.value
    assert v.figure.min_aspect_ratio == 1
    assert v.figure.max_aspect_ratio == 1


def test_show_axes(app, dataxyz):
    s = app.scatter2d('x', 'y', data=dataxyz)
    assert s.state.show_axes
    assert s.widget_show_axes.checked
    margin_initial = s.figure.fig_margin
    s.state.show_axes = False
    assert s.widget_show_axes.checked == False
    assert s.figure.fig_margin != margin_initial
    s.widget_show_axes.checked = True
    assert s.state.show_axes == True
    assert s.figure.fig_margin == margin_initial
