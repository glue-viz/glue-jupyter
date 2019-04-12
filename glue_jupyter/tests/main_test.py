import os

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

import glue_jupyter as gj

DATA = os.path.join(os.path.dirname(__file__), 'data')


def test_default_components(app, datax, dataxz, dataxyz):
    s = app.scatter2d(data=datax)
    assert s.state.x_att is datax.main_components[0]

    s = app.scatter2d(data=dataxz)
    assert s.state.x_att is dataxz.main_components[0]
    assert s.state.y_att is dataxz.main_components[1]

    s = app.scatter3d(data=datax)
    assert s.state.x_att is datax.main_components[0]

    s = app.scatter3d(data=dataxz)
    assert s.state.x_att is dataxz.main_components[0]
    assert s.state.y_att is dataxz.main_components[1]

    s = app.scatter3d(data=dataxyz)
    assert s.state.x_att is dataxyz.main_components[0]
    assert s.state.y_att is dataxyz.main_components[1]
    assert s.state.z_att is dataxyz.main_components[2]


def test_viewer_state(app, dataxyz):
    s = app.scatter2d('x', 'y', data=dataxyz, viewer_state=dict(x_att=dataxyz.id['y'], y_att=dataxyz.id['z'], x_min=-1, x_max=1))
    # direct argument have preference over the viewer_state
    assert s.state.x_att is dataxyz.id['x']
    assert s.state.y_att is dataxyz.id['y']
    assert s.state.x_min == -1
    assert s.state.x_max == 1

    # was testing with x_min, but it gets reset to hist_x_min
    s = app.histogram1d('y', data=dataxyz, viewer_state=dict(x_att=dataxyz.id['z'], hist_x_min=-1, hist_x_max=1))
    assert s.state.x_att is dataxyz.id['y']
    assert s.state.hist_x_min == -1
    assert s.state.hist_x_max == 1

    # x_min is used for the API, this sets viewer.state.hist_x_min/max which sets again viewer.state.x_min
    s = app.histogram1d('y', data=dataxyz, x_min=-2, x_max=2)
    assert s.state.x_att is dataxyz.id['y']
    assert s.state.hist_x_min == -2
    assert s.state.hist_x_max == 2
    assert s.state.x_min == -2
    assert s.state.x_max == 2


def test_layer_state(app, dataxyz):
    s = app.scatter2d(data=dataxyz, layer_state=dict(size=10))
    assert s.layers[0].state.size == 10
    # direct argument have preference over the layer_state
    s = app.scatter2d(data=dataxyz, size=11, layer_state=dict(size=10))
    assert s.layers[0].state.size == 11

    s = app.histogram1d('x', data=dataxyz, layer_state=dict(color='green'))
    assert s.layers[0].state.color == 'green'


def test_add_data_with_state(app, dataxz, dataxyz):
    s = app.scatter2d('x', 'z', data=dataxz, color='green')
    s.add_data(dataxyz, color='red', alpha=0.2, size=3.3)
    assert s.layers[0].state.color == 'green'
    assert s.layers[1].state.color == 'red'
    assert s.layers[1].state.alpha == 0.2
    assert s.layers[1].state.size == 3.3


def test_double_load_data(tmpdir):

    # Regression test for a bug that caused a crash when adding two datasets
    # with the same shape.

    filename = tmpdir.join('data1.csv').strpath

    with open(filename, 'w') as f:
        f.write('a,b\n1,2\n3,4\n5.6\n')

    app = gj.jglue()
    app.load_data(filename)
    app.load_data(filename)


def test_state_widget_notebook():

    with open(os.path.join(DATA, 'state_widgets.ipynb')) as f:
        nb = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    ep.preprocess(nb, {'metadata': {'path': DATA}})
