import pytest
import numpy as np

import glue_jupyter as gj
from glue.core import Data
from glue.core.component_link import ComponentLink
from glue.core.roi import PolygonalROI, Projected3dROI


@pytest.fixture#(scope="module")
def dataxyz():
    data = Data(x=[1, 2, 3], y=[2, 3, 4], z=[5, 6, 7], label="xyz data")
    return data

@pytest.fixture#(scope="module")
def dataxz():
    ox = 0
    oy = 1
    data = Data(x=[1 + ox, 2 + ox, 3 + ox], z=[2 + oy, 3 + oy, 4 + oy], label="xy data")
    return data

@pytest.fixture#(scope="module")
def data_volume():
    return gj.example_volume()

@pytest.fixture()#scope="module")
def data_image():
    return gj.example_image()

@pytest.fixture
def app(dataxyz, dataxz, data_volume, data_image):
    link1 = ['dataxyz.x'], ['dataxz.x'], lambda x: x
    link2 = ['dataxyz.y'], ['dataxz.z'], lambda y: y+1, lambda z: z-1
    app = gj.jglue(dataxyz=dataxyz, dataxz=dataxz, links=[link1, link2])
    app.add_data(data_volume=data_volume)
    app.add_data(data_image=data_image)
    link1 =  ComponentLink([data_image.id['Pixel Axis 0 [y]']], dataxyz.id['y'])
    link2 =  ComponentLink([data_image.id['Pixel Axis 1 [x]']], dataxyz.id['x'])
    app.data_collection.add_link([link1, link2])
    link1 =  ComponentLink([data_volume.id['Pixel Axis 0 [z]']], dataxyz.id['z'])
    link2 =  ComponentLink([data_volume.id['Pixel Axis 1 [y]']], dataxyz.id['y'])
    link3 =  ComponentLink([data_volume.id['Pixel Axis 2 [x]']], dataxyz.id['x'])
    app.data_collection.add_link([link1, link2, link3])
    return app

def test_app(app, dataxyz, dataxz):
    assert app._data[0] in [dataxyz, dataxz]
    assert app.widget_selection_mode.index == 0
    assert len(app.widget_subset_groups.options) == 0
    assert len(app.widget_subset_groups.index) == 0
    app.subset_mode_and()
    assert app.widget_selection_mode.index == 2
    app.subset_mode_replace()
    assert app.widget_selection_mode.index == 0
    assert len(app.widget_subset_groups.index) == 0
    app.subset_lasso2d(dataxyz.id['x'], dataxyz.id['y'], [0.5, 2.5, 2.5, 0.5], [1, 1, 3.5, 3.5])

    assert len(app.widget_subset_groups.options) == len(app.data_collection.subset_groups)
    assert len(app.widget_subset_groups.index) == 0

    app.session.edit_subset_mode.edit_subset = [app.data_collection.subset_groups[0]]
    assert len(app.widget_subset_groups.index) == 1
    assert app.widget_subset_groups.index == (0,)

    app.session.edit_subset_mode.edit_subset = []
    assert len(app.widget_subset_groups.index) == 0
    assert app.widget_subset_groups.index == ()

    app.widget_subset_groups.index = (0,)
    assert app.session.edit_subset_mode.edit_subset == [app.data_collection.subset_groups[0]]

    app.session.edit_subset_mode.edit_subset = []
    assert len(app.widget_subset_groups.index) == 0
    assert app.data_collection[0].subsets[0]['x'].tolist() == [1, 2]
    assert app.data_collection[0].subsets[0]['y'].tolist() == [2, 3]
    assert app.data_collection[0].subsets[0]['z'].tolist() == [5, 6]


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

    s.brush_x.brushing = True
    s.brush_x.selected = [2.5, 3.5]
    s.brush_x.brushing = False

    assert len(s.layers) == 3
    assert s.layers[2].bins.tolist() == [1.5, 2.5, 3.5, 4.5]
    assert s.layers[2].hist.tolist() == [0, 1, 0]


    # s.state.hist_n_bin = 6
    # assert s.layers[2].bins.tolist() == [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
    # assert s.layers[2].hist.tolist() == [0, 1, 0, 0, 0, 0]


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


def test_scatter2d_and_histogram(app, dataxyz):
    s = app.scatter2d('x', 'y', data=dataxyz)
    h = app.histogram1d('x', data=dataxyz)
    s.brush.brushing = True
    s.brush.selected = [(1.5, 3.5), (3.5, 5)]
    s.brush.brushing = False
    assert len(s.layers) == 2
    import glue.core.subset
    assert isinstance(s.layers[1].layer.subset_state, glue.core.subset.RoiSubsetState)



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

    assert len(s.tab.children) == 2
    app.subset('test', dataxyz.id['x'] > 2)
    assert len(s.layers) == 2
    assert len(s.tab.children) == 3
    assert s.layers[1].layer['x'].tolist() == [3]
    assert s.layers[1].layer['y'].tolist() == [4]
    assert s.layers[1].layer['z'].tolist() == [7]

    assert s.layers[1].scatter.x.tolist() == [1, 2, 3]
    assert s.layers[1].scatter.y.tolist() == [2, 3, 4]
    assert s.layers[1].scatter.z.tolist() == [5, 6, 7]
    assert s.layers[1].scatter.selected == [2]

    s.state.x_att = dataxyz.id['y']
    s.state.y_att = dataxyz.id['z']
    s.state.z_att = dataxyz.id['x']
    assert s.layers[1].scatter.x.tolist() == [2, 3, 4]
    assert s.layers[1].scatter.y.tolist() == [5, 6, 7]
    assert s.layers[1].scatter.z.tolist() == [1, 2, 3]
    assert s.layers[1].scatter.selected == [2]

    assert s.widgets_axis[0].value == 'y'
    assert s.widgets_axis[1].value == 'z'
    assert s.widgets_axis[2].value == 'x'

    size_previous = s.layers[0].scatter.size
    s.layers[0].state.size_mode = 'Linear'
    assert s.layers[0].scatter.size is not size_previous

    # check response to size_att
    size_previous = s.layers[0].scatter.size
    s.layers[0].state.size_att = dataxyz.id['z']
    assert s.layers[0].scatter.size is not size_previous

    # check response to size_vmin
    size_previous = s.layers[0].scatter.size
    s.layers[0].state.size_vmax = s.layers[0].state.size_vmax * 2
    assert s.layers[0].scatter.size is not size_previous

    # test quiver
    layer = s.layers[0]
    assert not layer.quiver.visible
    layer.state.vector_visible = True
    assert layer.quiver.visible

def test_roi3d(dataxyz):
    roi_2d = PolygonalROI(vx=[0.5, 2.5, 2.5, 0.5], vy=[1, 1, 3.5, 3.5])
    roi = Projected3dROI(roi_2d, projection_matrix=np.eye(4))
    assert roi.contains(dataxyz['x'], dataxyz['y']).tolist() == [True, True, False]

    roi_2d = PolygonalROI(vx=[1.5, 3.5, 3.5, 1.5], vy=[4, 4, 6.5, 6.5])
    roi = Projected3dROI(roi_2d, projection_matrix=xyzw2yxzw)
    assert roi.contains3d(dataxyz['x'], dataxyz['y'], dataxyz['z']).tolist() == [True, True, False]

def test_lasso3d(app, dataxyz):
    s = app.scatter3d('x', 'y', 'z', data=dataxyz)
    s.figure.matrix_world = np.eye(4).ravel().tolist()
    s.figure.matrix_projection = np.eye(4).ravel().tolist()
    # similar to the roi3d test above, and this is the format that ipyvolume send back
    data = {'type': 'lasso', 'device': zip([0.5, 2.5, 2.5, 0.5], [1, 1, 3.5, 3.5])}
    # fake the callback
    s.figure._selection_handlers(data)
    assert len(s.layers) == 2
    assert s.layers[1].layer['x'].tolist() == [1, 2]
    assert s.layers[1].layer['y'].tolist() == [2, 3]
    assert s.layers[1].layer['z'].tolist() == [5, 6]

    data = {'type': 'circle', 'device': {'begin': [2.5, 3.5], 'end': [3.1, 4.1]}}
    # fake the callback
    s.figure._selection_handlers(data)
    assert len(s.layers) == 2
    assert s.layers[1].layer['x'].tolist() == [2, 3]
    assert s.layers[1].layer['y'].tolist() == [3, 4]
    assert s.layers[1].layer['z'].tolist() == [6, 7]


    data = {'type': 'rectangle', 'device': {'begin': [0, 0], 'end': [2.1, 3.1]}}
    # fake the callback
    s.figure._selection_handlers(data)
    assert len(s.layers) == 2
    assert s.layers[1].layer['x'].tolist() == [1, 2]
    assert s.layers[1].layer['y'].tolist() == [2, 3]
    assert s.layers[1].layer['z'].tolist() == [5, 6]

def test_volshow(app, data_volume, dataxyz):
    assert data_volume in app.data_collection
    v = app.volshow(data=data_volume)

    data = {'type': 'lasso', 'device': zip([0.5, 2.5, 2.5, 0.5], [1, 1, 3.5, 3.5])}
    # fake the callback
    v.figure._selection_handlers(data)
    assert len(v.layers) == 2
    v.add_data(dataxyz)
    assert len(v.layers) == 4

    # assert s.layers[1].layer['x'].tolist() == [1, 2]
    # assert s.layers[1].layer['y'].tolist() == [2, 3]
    # assert s.layers[1].layer['z'].tolist() == [5, 6]

def test_imshow(app, data_image, dataxyz):
    assert data_image in app.data_collection
    v = app.imshow(data=data_image)

    v.add_data(dataxyz)

    assert len(v.layers) == 2
    v.brush.brushing = True
    v.brush.selected = [(1.5, 3.5), (300.5, 550)]
    v.brush.brushing = False

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
