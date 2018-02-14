import pytest
import numpy as np

import glue_jupyter as gj
from glue.core import Data
from glue_jupyter.roi3d import PolygonalProjected3dROI


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

xyzw2yxzw = np.array([
             [0, 1, 0, 0],
             [0, 0, 1, 0],
             [1, 0, 0, 0],
             [0, 0, 0, 1]
            ])

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

    s.state.y_att = 'z'
    assert s.layers[1].scatter.x.tolist() == [1, 2, 3]
    assert s.layers[1].scatter.y.tolist() == [5, 6, 7]
    assert s.layers[1].scatter.selected == [2]

def test_scatter2d_brush(app, dataxyz, dataxz):
    s = app.scatter2d('x', 'y', data=dataxyz)

    # 1d x brushing
    s.button_action.value = 'brush x'
    s.brush_x.brushing = True
    s.brush_x.selected = [1.5, 3.5]
    s.brush_x.brushing = False
    assert len(s.layers) == 2
    assert s.layers[1].layer['x'].tolist() == [2, 3]
    assert s.layers[1].layer['y'].tolist() == [3, 4]
    assert s.layers[1].layer['z'].tolist() == [6, 7]

    assert s.layers[1].scatter.x.tolist() == [1, 2, 3]
    assert s.layers[1].scatter.y.tolist() == [2, 3, 4]
    assert s.layers[1].scatter.selected == [1, 2]

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

    # nothing should change when we change modes
    s.button_action.value = 'brush'
    assert s.layers[1].scatter.selected == [2]
    s.button_action.value = 'brush x'
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
    assert s.state.z_min == 5
    assert s.state.z_max == 7

    app.subset('test', dataxyz.id['x'] > 2)
    assert len(s.layers)
    assert s.layers[1].layer['x'].tolist() == [3]
    assert s.layers[1].layer['y'].tolist() == [4]
    assert s.layers[1].layer['z'].tolist() == [7]

    assert s.layers[1].scatter.x.tolist() == [1, 2, 3]
    assert s.layers[1].scatter.y.tolist() == [2, 3, 4]
    assert s.layers[1].scatter.z.tolist() == [5, 6, 7]
    assert s.layers[1].scatter.selected == [2]

    s.state.x_att = 'y'
    s.state.y_att = 'z'
    s.state.z_att = 'x'
    assert s.layers[1].scatter.x.tolist() == [2, 3, 4]
    assert s.layers[1].scatter.y.tolist() == [5, 6, 7]
    assert s.layers[1].scatter.z.tolist() == [1, 2, 3]
    assert s.layers[1].scatter.selected == [2]

def test_roi3d(dataxyz):
    roi = PolygonalProjected3dROI(vx=[0.5, 2.5, 2.5, 0.5], vy=[1, 1, 3.5, 3.5], projection_matrix=np.eye(4))
    assert roi.contains(dataxyz['x'], dataxyz['y']).tolist() == [True, True, False]

    # xyzw2yxzw = [[0, 0, 1, 0],
    #              [1, 0, 0, 0],
    #              [0, 1, 0, 0],
    #              [0, 0, 0, 1]
    #             ]
    roi = PolygonalProjected3dROI(vx=[1.5, 3.5, 3.5, 1.5], vy=[4, 4, 6.5, 6.5], projection_matrix=xyzw2yxzw)
    assert roi.contains3d(dataxyz['x'], dataxyz['y'], dataxyz['z']).tolist() == [True, True, False]

def test_lasso3d(app, dataxyz):
    s = app.scatter3d('x', 'y', 'z', data=dataxyz)
    s.figure.matrix_world = np.eye(4).ravel().tolist()
    s.figure.matrix_projection = np.eye(4).ravel().tolist()
    # similar to the roi3d test above, and this is the format that ipyvolume send back
    data = {'device': zip([0.5, 2.5, 2.5, 0.5], [1, 1, 3.5, 3.5])}
    # fake the callback
    s.figure._lasso_handlers(data)
    assert len(s.layers) == 2
    assert s.layers[1].layer['x'].tolist() == [1, 2]
    assert s.layers[1].layer['y'].tolist() == [2, 3]
    assert s.layers[1].layer['z'].tolist() == [5, 6]
