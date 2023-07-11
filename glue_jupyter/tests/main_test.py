import os

import pytest
import nbformat
import numpy as np
from nbconvert.preprocessors import ExecutePreprocessor

from glue.core import Data
from glue.core.autolinking import find_possible_links

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
    s = app.scatter2d(x='x', y='y', data=dataxyz, viewer_state=dict(x_att=dataxyz.id['y'],
                                                                    y_att=dataxyz.id['z'],
                                                                    x_min=-1, x_max=1))
    # direct argument have preference over the viewer_state
    assert s.state.x_att is dataxyz.id['x']
    assert s.state.y_att is dataxyz.id['y']
    assert s.state.x_min == -1
    assert s.state.x_max == 1

    # was testing with x_min, but it gets reset to hist_x_min
    s = app.histogram1d(x='y', data=dataxyz, viewer_state=dict(x_att=dataxyz.id['z'],
                                                               hist_x_min=-1, hist_x_max=1))
    assert s.state.x_att is dataxyz.id['y']
    assert s.state.hist_x_min == -1
    assert s.state.hist_x_max == 1

    # x_min is used for the API, this sets viewer.state.hist_x_min/max which
    # sets again viewer.state.x_min
    s = app.histogram1d(x='y', data=dataxyz, x_min=-2, x_max=2)
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

    s = app.histogram1d(x='x', data=dataxyz, layer_state=dict(color='green'))
    assert s.layers[0].state.color == 'green'


def test_add_data_with_state(app, dataxz, dataxyz):
    s = app.scatter2d(x='x', y='z', data=dataxz, color='green')
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


INVALID_TYPE_EXC = """
The data argument should either be a glue data object or the name of a dataset.
The following datasets are available:

  * 'mydata1'
  * 'mydata2'
"""

INVALID_NAME_EXC = """
'mydata3' is not a valid dataset name. The following datasets are available:

  * 'mydata1'
  * 'mydata2'
"""


VIEWERS = ['histogram1d', 'scatter2d', 'scatter3d', 'imshow', 'profile1d', 'volshow']


@pytest.mark.parametrize('viewer_name', VIEWERS)
def test_data_names(app, viewer_name):

    # Make sure that we can refer to datasets by name in the viewers, and check
    # the error message if an invalid object is passed.

    data1 = Data(x=np.ones((2, 3, 4)))
    data2 = Data(y=np.ones((2, 3, 4)))

    app.data_collection.clear()

    app.add_data(mydata1=data1)
    app.add_data(mydata2=data2)

    viewer_method = getattr(app, viewer_name)

    # If we pass something that isn't a valid data object or a string we should
    # get an error:

    with pytest.raises(TypeError) as exc:
        viewer_method(data=1 + 1j)
    assert exc.value.args[0] == INVALID_TYPE_EXC.strip()

    # If the name of the dataset doesn't exist, we also give an explicit
    # error.

    with pytest.raises(ValueError) as exc:
        viewer_method(data='mydata3')
    assert exc.value.args[0] == INVALID_NAME_EXC.strip()

    # Passing a valid name should work

    hist = viewer_method(data='mydata1')

    # We can check for the validation again when calling add_data

    with pytest.raises(TypeError) as exc:
        hist.add_data(data=1 + 1j)
    assert exc.value.args[0] == INVALID_TYPE_EXC.strip()

    with pytest.raises(ValueError) as exc:
        hist.add_data(data='mydata3')
    assert exc.value.args[0] == INVALID_NAME_EXC.strip()


def test_no_data(dataxz, dataxyz):

    app = gj.jglue()

    with pytest.raises(ValueError, match='No dataset is present'):
        app.scatter2d()

    app.add_data(dataxz)
    app.scatter2d()

    app.add_data(dataxyz)
    with pytest.raises(ValueError, match='There is more than one dataset'):
        app.scatter2d()


def test_plugins():

    # Make sure that glue plugins are correctly loaded, by checking that the
    # WCS autolinker works.

    from astropy.wcs import WCS

    app = gj.jglue()

    data1 = Data(label='test1')
    data1.coords = WCS(naxis=2)
    data1.coords.wcs.ctype = 'RA---TAN', 'DEC--TAN'
    data1.coords.wcs.set()
    data1['x'] = np.ones((2, 3))

    data2 = Data(label='test1')
    data2.coords = WCS(naxis=2)
    data2.coords.wcs.ctype = 'GLON-CAR', 'GLAT-CAR'
    data2.coords.wcs.set()
    data2['y'] = np.ones((2, 3))

    app.add_data(data1=data1)
    app.add_data(data2=data2)

    links = find_possible_links(app.data_collection)

    assert 'Astronomy WCS' in links


def test_viewers(app, datax, dataxz):

    assert app.viewers == []

    s1 = app.scatter2d(data=datax)
    assert len(app.viewers) == 1
    assert app.viewers[0] is s1

    s2 = app.scatter2d(data=dataxz)
    assert len(app.viewers) == 2
    assert app.viewers[0] is s1
    assert app.viewers[1] is s2
