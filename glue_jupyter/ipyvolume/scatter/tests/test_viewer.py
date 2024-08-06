def test_scatter3d_nd(app, data_4d):
    # Make sure that things work correctly with arrays that have more than
    # one dimension.
    app.add_data(data_4d)
    scatter = app.scatter3d(x='x', y='x', z='x', data=data_4d)
    scatter.state.layers[0].vector_visible = True
    scatter.state.layers[0].size_mode = 'Linear'
    scatter.state.layers[0].cmap_mode = 'Linear'


def test_scatter3d_categorical(app, datacat):
    # Make sure that things work correctly with arrays that have categorical
    # components - for now these are skipped, until we figure out how to
    # show the correct categorical labels on the axes.
    app.add_data(datacat)
    scatter = app.scatter3d(data=datacat)
    assert str(scatter.state.x_att) == 'a'
    assert str(scatter.state.y_att) == 'b'
    assert str(scatter.state.z_att) == 'b'


def test_non_hex_colors(app, dataxyz):

    # Make sure non-hex colors such as '0.4' and 'red', which are valid
    # matplotlib colors, work as expected.

    viewer = app.scatter3d(data=dataxyz)
    dataxyz.style.color = '0.3'
    dataxyz.style.color = 'indigo'

    app.subset('test', dataxyz.id['x'] > 1)
    viewer.layer_options.selected = 1
    dataxyz.subsets[0].style.color = '0.5'
    dataxyz.subsets[0].style.color = 'purple'


def test_labels(app, dataxyz):
    # test the syncing of attributes to labels
    app.add_data(dataxyz)
    scatter = app.scatter3d(data=dataxyz)
    assert str(scatter.state.x_att) == 'x'
    assert scatter.figure.zlabel == 'x'
    assert str(scatter.state.y_att) == 'y'
    assert scatter.figure.xlabel == 'y'
    assert str(scatter.state.z_att) == 'z'
    assert scatter.figure.ylabel == 'z'

    scatter.state.x_att = dataxyz.id['y']
    assert scatter.figure.zlabel == 'y'
    scatter.state.y_att = dataxyz.id['z']
    assert scatter.figure.xlabel == 'z'
    scatter.state.z_att = dataxyz.id['x']
    assert scatter.figure.ylabel == 'x'
