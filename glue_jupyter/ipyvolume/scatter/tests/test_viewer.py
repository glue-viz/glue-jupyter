def test_scatter3d_nd(app, data_4d):
    # Make sure that things work correctly with arrays that have more than
    # one dimension.
    app.add_data(data_4d)
    scatter = app.scatter3d('x', 'x', 'x', data=data_4d)
    scatter.state.layers[0].vector_visible = True
    scatter.state.layers[0].size_mode = 'Linear'
    scatter.state.layers[0].cmap_mode = 'Linear'
