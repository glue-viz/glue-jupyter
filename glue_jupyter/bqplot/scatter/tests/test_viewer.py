def test_scatter2d_nd(app, data_4d):
    # Regression test for a bug that meant that arrays with more than one
    # dimension did not work correctly.
    app.add_data(data_4d)
    scatter = app.scatter2d('x', 'x', data=data_4d)
    scatter.state.layers[0].vector_visible = True
    scatter.state.layers[0].size_mode = 'Linear'
    scatter.state.layers[0].cmap_mode = 'Linear'


def test_scatter2d_categorical(app, datacat):
    # Make sure that things work correctly with arrays that have categorical
    # components - we use the numerical codes for these. In future we should
    # make sure that we show the correct labels on the axes.
    app.add_data(datacat)
    scatter = app.scatter2d(data=datacat)
    scatter.state.layers[0].vector_visible = True
    scatter.state.layers[0].size_mode = 'Linear'
    scatter.state.layers[0].cmap_mode = 'Linear'
    assert scatter.state.x_att.label == 'a'
    assert scatter.state.y_att.label == 'b'
