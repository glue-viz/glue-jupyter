import os

import nbformat
import numpy as np
from glue.core.roi import PolygonalROI, Projected3dROI
from nbconvert.preprocessors import ExecutePreprocessor

DATA = os.path.join(os.path.dirname(__file__), 'data')

xyzw2yxzw = np.array([
             [0, 1, 0, 0],
             [0, 0, 1, 0],
             [1, 0, 0, 0],
             [0, 0, 0, 1]
            ])


def test_scatter3d(app, dataxyz, dataxz):
    s = app.scatter3d(x='x', y='y', z='z', data=dataxyz)
    assert s.state.x_att == 'x'
    assert s.state.y_att == 'y'
    # assert s.state.z_att == 'z'

    assert s.state.x_min == 1
    assert s.state.x_max == 3
    assert s.state.y_min == 2
    assert s.state.y_max == 4
    assert s.state.z_min == 5
    assert s.state.z_max == 7

    assert len(s.layer_options.layers) == 1
    app.subset('test', dataxyz.id['x'] > 2)
    assert len(s.layers) == 2
    assert len(s.layer_options.layers) == 2
    assert s.layers[1].layer['x'].tolist() == [3]
    assert s.layers[1].layer['y'].tolist() == [4]
    assert s.layers[1].layer['z'].tolist() == [7]

    assert s.layers[1].scatter.x.tolist() == [1, 2, 3]
    assert s.layers[1].scatter.z.tolist() == [2, 3, 4]
    assert s.layers[1].scatter.y.tolist() == [5, 6, 7]
    assert s.layers[1].scatter.selected == [2]

    s.state.x_att = dataxyz.id['y']
    s.state.y_att = dataxyz.id['z']
    s.state.z_att = dataxyz.id['x']
    assert s.layers[1].scatter.x.tolist() == [2, 3, 4]
    assert s.layers[1].scatter.z.tolist() == [5, 6, 7]
    assert s.layers[1].scatter.y.tolist() == [1, 2, 3]
    assert s.layers[1].scatter.selected == [2]

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


def test_scatter3d_cmap_mode(app, dataxyz):

    s = app.scatter3d(x='x', y='y', data=dataxyz)
    l1 = s.layers[0]

    layer_widget = s.layer_options.layers[-1]['layer_panel']

    assert l1.state.cmap_mode == 'Fixed', 'expected default value'
    assert l1.state.cmap_name == 'Gray'

    assert l1.scatter.color.shape == (), 'numpy scalar'
    l1.state.cmap_att = 'x'
    l1.state.cmap_mode = 'Linear'
    assert layer_widget.widget_color.widget_cmap_mode.label == 'Linear'
    assert l1.state.cmap_name == 'Gray'
    l1.state.cmap_vmin = 0
    l1.state.cmap_vmax = 10
    assert l1.scatter.color.shape == (3, 4)
    assert l1.scatter.color is not None

    layer_widget.widget_color.widget_cmap.label = 'Viridis'
    assert l1.state.cmap_name == 'Viridis'
    assert layer_widget.widget_color.widget_cmap.label == 'Viridis'

    layer_widget.widget_color.widget_cmap.label = 'Gray'
    assert layer_widget.widget_color.widget_cmap.label == 'Gray'
    assert l1.state.cmap_name == 'Gray'


def test_roi3d(dataxyz):

    roi_2d = PolygonalROI(vx=[0.5, 2.5, 2.5, 0.5], vy=[1, 1, 3.5, 3.5])
    roi = Projected3dROI(roi_2d, projection_matrix=np.eye(4))
    assert roi.contains(dataxyz['x'], dataxyz['y']).tolist() == [True, True, False]

    roi_2d = PolygonalROI(vx=[1.5, 3.5, 3.5, 1.5], vy=[4, 4, 6.5, 6.5])
    roi = Projected3dROI(roi_2d, projection_matrix=xyzw2yxzw)
    assert roi.contains3d(dataxyz['x'], dataxyz['y'], dataxyz['z']).tolist() == [True, True, False]


def test_lasso3d(app, dataxyz):
    s = app.scatter3d(x='x', y='y', z='z', data=dataxyz)
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


def test_scatter3d_multiple_subsets(app, data_unlinked, dataxyz):
    # Make sure that things work fine if an incompatible subset is added
    viewer = app.scatter3d(x='x', y='y', z='z', data=dataxyz)
    app.subset('test1', dataxyz.id['x'] > 1)
    app.subset('test2', data_unlinked.id['a'] > 1)
    assert viewer.layers[0].enabled
    assert viewer.layers[1].enabled
    assert not viewer.layers[2].enabled


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


def test_volshow_multiple_subsets(app, data_unlinked, data_volume):
    # Make sure that things work fine if an incompatible subset is added
    viewer = app.volshow(data=data_volume)
    app.subset('test1', data_volume.id['intensity'] > 1)
    app.subset('test2', data_unlinked.id['a'] > 1)
    assert viewer.layers[0].enabled
    assert viewer.layers[1].enabled
    assert not viewer.layers[2].enabled


def test_notebook():

    # Run an actual notebook

    with open(os.path.join(DATA, 'ipyvolume.ipynb')) as f:
        nb = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    ep.preprocess(nb, {'metadata': {'path': DATA}})
