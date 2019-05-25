def test_scatter3d_nd(app, data_4d):
    # Make sure that things work correctly with arrays that have more than
    # one dimension.
    app.add_data(data_4d)
    scatter = app.scatter3d('x', 'x', 'x', data=data_4d)
    scatter.state.layers[0].vector_visible = True
    scatter.state.layers[0].size_mode = 'Linear'
    scatter.state.layers[0].cmap_mode = 'Linear'


def test_scatter3d_categorical(app, datacat):
    # Make sure that things work correctly with arrays that have categorical
    # components - for now these are skipped, until we figure out how to
    # show the correct categorical labels on the axes.
    app.add_data(datacat)
    scatter = app.scatter3d(data=datacat)
    assert scatter.state.x_att.label == 'a'
    assert scatter.state.y_att.label == 'b'
    assert scatter.state.z_att.label == 'b'
