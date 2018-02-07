import pytest
import glue_jupyter as gj
from glue.core import Data


@pytest.fixture
def dataxyz():
    data = Data(x=[1, 2, 3], y=[2, 3, 4], z=[5, 6, 7], label="xyz data")
    return data

@pytest.fixture
def dataxz():
    ox = 0
    oy = 1
    data = Data(x=[1 + ox, 2 + ox, 3 + ox], z=[2 + oy, 3 + oy, 4 + oy], label="xy data")
    return data


@pytest.fixture
def app(dataxyz, dataxz):
    link1 = ['dataxyz.x'], ['dataxz.x'], lambda x: x
    link2 = ['dataxyz.y'], ['dataxz.z'], lambda y: y+1, lambda z: z-1
    return gj.jglue(dataxyz=dataxyz, dataxz=dataxz, links=[link1, link2])

def test_app(app, dataxyz, dataxz):
    assert app._data[0] in [dataxyz, dataxz]

def test_scatter2d(app, dataxyz, dataxz):
    s = app.scatter2d('x', 'y', data=dataxyz)
    assert s.state.x_att == 'x'
    assert s.state.y_att == 'y'

    assert s.state.x_min == 1
    assert s.state.x_max == 3
    assert s.state.y_min == 2
    assert s.state.y_max == 4

    # test when we swap x and x
    s = app.scatter2d('y', 'x', data=dataxyz)
    assert s.state.x_att == 'y'
    assert s.state.y_att == 'x'
    assert s.state.y_min == 1
    assert s.state.y_max == 3
    assert s.state.x_min == 2
    assert s.state.x_max == 4

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

def test_scatter2d_brush(app, dataxyz, dataxz):
    s = app.scatter2d('x', 'y', data=dataxyz)
    # format is (x1, y1), (x2, y2)
    s.brush.brushing = True
    s.brush.selected = [(1.5, 3.5), (3.5, 5)]
    s.brush.brushing = False
    assert len(s.layers) == 2
    assert s.layers[1].layer['x'].tolist() == [3]
    assert s.layers[1].layer['y'].tolist() == [4]
    assert s.layers[1].layer['z'].tolist() == [7]

    assert s.layers[1].scatter.x.tolist() == [1, 2, 3]
    assert s.layers[1].scatter.y.tolist() == [2, 3, 4]
    assert s.layers[1].scatter.selected == [2]

def test_scatter2d_properties(app, dataxyz, dataxz):
    s = app.scatter2d('x', 'y', data=dataxyz)
    l1 = s.layers[0]
    l1.state.color = 'green'
    assert l1.scatter.colors == ['green']
    l1.scatter.colors = ['orange']
    assert l1.state.color == 'orange'


def test_scatter3d(app, dataxyz, dataxz):
    s = app.scatter3d('x', 'y', 'z', data=dataxyz)
    assert s.state.x_att == 'x'
    assert s.state.y_att == 'y'
    # assert s.state.z_att == 'z'

    assert s.state.x_min == 1
    assert s.state.x_max == 3
    assert s.state.y_min == 2
    assert s.state.y_max == 4
    # assert s.state.z_min == 5
    # assert s.state.z_max == 7

    app.subset('test', dataxyz.id['x'] > 2)
    assert len(s.layers)
    assert s.layers[1].layer['x'].tolist() == [3]
    assert s.layers[1].layer['y'].tolist() == [4]
    assert s.layers[1].layer['z'].tolist() == [7]

    assert s.layers[1].scatter.x.tolist() == [3]
    assert s.layers[1].scatter.y.tolist() == [4]

