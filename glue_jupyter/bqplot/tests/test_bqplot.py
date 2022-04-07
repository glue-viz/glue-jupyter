import os
import nbformat
import numpy as np
from numpy.testing import assert_allclose
from nbconvert.preprocessors import ExecutePreprocessor
from glue.core import Data
from glue.core.roi import EllipticalROI

DATA = os.path.join(os.path.dirname(__file__), 'data')


def test_histogram1d(app, dataxyz):
    s = app.histogram1d(x='y', data=dataxyz)
    assert s.state.x_att == 'y'
    assert len(s.layers) == 1
    assert s.layers[0].layer['y'].tolist() == [2, 3, 4]
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

    tool = s.toolbar.tools['bqplot:xrange']
    tool.activate()
    tool.interact.brushing = True
    tool.interact.selected = [2.5, 3.5]
    tool.interact.brushing = False

    assert len(s.layers) == 3
    assert s.layers[2].bins.tolist() == [1.5, 2.5, 3.5, 4.5]
    assert s.layers[2].hist.tolist() == [0, 1, 0]

    # s.state.hist_n_bin = 6
    # assert s.layers[2].bins.tolist() == [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
    # assert s.layers[2].hist.tolist() == [0, 1, 0, 0, 0, 0]


def test_histogram1d_multiple_subsets(app, data_unlinked, datax):
    # Make sure that things work fine if an incompatible subset is added
    viewer = app.histogram1d(x='x', data=datax)
    app.subset('test1', datax.id['x'] > 1)
    app.subset('test2', data_unlinked.id['a'] > 1)
    assert viewer.layers[0].enabled
    assert viewer.layers[1].enabled
    assert not viewer.layers[2].enabled


def test_interact(app, dataxyz):
    s = app.scatter2d(x='x', y='y', data=dataxyz)
    # s.widget_menu_select_x.value = True
    # s.widget_menu_select_x.click()# = True
    tool = s.toolbar.tools['bqplot:xrange']
    s.toolbar.active_tool = tool
    # Note that we need to access 'next' because the default interact
    # is a MouseInteraction and tools are activated/deactivated via the
    # 'next' property.
    assert s.figure.interaction.next == tool.interact


def test_scatter2d(app, dataxyz, dataxz):
    s = app.scatter2d(x='x', y='y', data=dataxyz)
    assert s.state.x_att == 'x'
    assert s.state.y_att == 'y'

    # assert s.state.x_min == 1
    # assert s.state.x_max == 3
    # assert s.state.y_min == 2
    # assert s.state.y_max == 4

    # test when we swap x and x
    s = app.scatter2d(x='y', y='x', data=dataxyz)
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


def test_scatter2d_density(app, dataxyz):
    s = app.scatter2d(x='x', y='y', data=dataxyz)
    s.layers[0].state.points_mode = 'density'
    assert s.layers[0].state.density_map is True

    s.state.x_min = 0.9
    s.state.x_max = 3.1
    s.state.y_min = 1.9
    s.state.y_max = 5.1
    assert s.layers[0].state.density_map is True
    s.layers[0].state.bins = 2
    assert s.layers[0].image.image.tolist() == [[2.0, 0], [0, 1.0]]


def test_scatter2d_subset(app, dataxyz, dataxz):
    s = app.scatter2d(x='x', y='y', data=dataxyz)
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


def test_scatter2d_multiple_subsets(app, data_unlinked, dataxz):
    # Make sure that things work fine if an incompatible subset is added
    viewer = app.scatter2d(x='x', y='z', data=dataxz)
    app.subset('test1', dataxz.id['x'] > 1)
    app.subset('test2', data_unlinked.id['a'] > 1)
    assert viewer.layers[0].enabled
    assert viewer.layers[1].enabled
    assert not viewer.layers[2].enabled


def test_scatter2d_brush(app, dataxyz, dataxz):
    s = app.scatter2d(x='x', y='y', data=dataxyz)

    # 1d x brushing
    tool1d = s.toolbar.tools['bqplot:xrange']
    tool1d.activate()
    tool1d.interact.brushing = True
    tool1d.interact.selected = [1.5, 3.5]
    tool1d.interact.brushing = False

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
    # format of 'selected' (x1, y1), (x2, y2)
    tool2d = s.toolbar.tools['bqplot:rectangle']
    tool2d.activate()
    tool2d.interact.brushing = True
    tool2d.interact.selected = [(2.5, 2.5), (3.5, 4.5)]
    tool2d.interact.brushing = False

    assert len(s.layers) == 2
    assert s.layers[1].layer['x'].tolist() == [3]
    assert s.layers[1].layer['y'].tolist() == [4]
    assert s.layers[1].layer['z'].tolist() == [7]

    assert s.layers[1].scatter.x.tolist() == [1, 2, 3]
    assert s.layers[1].scatter.y.tolist() == [2, 3, 4]
    assert s.layers[1].scatter.selected == [2]

    # nothing should change when we change modes
    s.toolbar.active_tool = tool1d
    assert s.layers[1].scatter.selected == [2]
    s.toolbar.active_tool = tool2d
    assert s.layers[1].scatter.selected == [2]

    # 2d brushing
    # format of 'selected' (x1, y1), (x2, y2)
    tool_circle = s.toolbar.tools['bqplot:circle']
    tool_circle.activate()
    tool_circle.interact.brushing = True
    tool_circle.interact.selected = [(2.5, 2.5), (3.5, 4.5)]
    tool_circle.interact.brushing = False

    assert len(s.layers) == 2
    assert s.layers[1].layer['x'].tolist() == [3]
    assert s.layers[1].layer['y'].tolist() == [4]
    assert s.layers[1].layer['z'].tolist() == [7]

    assert s.layers[1].scatter.x.tolist() == [1, 2, 3]
    assert s.layers[1].scatter.y.tolist() == [2, 3, 4]
    assert s.layers[1].scatter.selected == [2]

    # nothing should change when we change modes
    s.toolbar.active_tool = tool1d
    assert s.layers[1].scatter.selected == [2]
    s.toolbar.active_tool = tool_circle
    assert s.layers[1].scatter.selected == [2]


def test_scatter2d_properties(app, dataxyz, dataxz):
    s = app.scatter2d(x='x', y='y', data=dataxyz)
    l1 = s.layers[0]
    l1.state.color = 'green'
    assert l1.scatter.colors == ['#008000']


def test_scatter2d_cmap_mode(app, dataxyz):
    s = app.scatter2d(x='x', y='y', data=dataxyz)
    l1 = s.layers[0]
    assert l1.state.cmap_mode == 'Fixed', 'expected default value'
    assert l1.state.cmap_name == 'Gray'

    assert l1.scatter.color is None
    l1.state.cmap_att = 'x'
    l1.state.cmap_mode = 'Linear'
    assert l1.state.cmap_name == 'Gray'
    l1.state.cmap_vmin = 0
    l1.state.cmap_vmax = 10
    assert l1.scatter.color is not None


def test_scatter2d_and_histogram(app, dataxyz):
    s = app.scatter2d(x='x', y='y', data=dataxyz)
    h = app.histogram1d(x='x', data=dataxyz)  # noqa
    tool = s.toolbar.tools['bqplot:rectangle']
    tool.activate()
    tool.interact.brushing = True
    tool.interact.selected = [(1.5, 3.5), (3.5, 5)]
    tool.interact.brushing = False
    assert len(s.layers) == 2
    import glue.core.subset
    assert isinstance(s.layers[1].layer.subset_state,
                      glue.core.subset.RoiSubsetState)


def test_imshow(app, data_image, dataxyz):
    assert data_image in app.data_collection
    v = app.imshow(data=data_image)

    v.add_data(dataxyz)

    assert len(v.layers) == 2

    tool = v.toolbar.tools['bqplot:rectangle']
    tool.activate()
    tool.interact.brushing = True
    tool.interact.selected = [(1.5, 3.5), (300.5, 550)]
    tool.interact.brushing = False

    assert len(v.layers) == 4


def test_imshow_circular_brush(app, data_image):

    v = app.imshow(data=data_image)
    v.state.aspect = 'auto'

    tool = v.toolbar.tools['bqplot:circle']
    tool.activate()
    tool.interact.brushing = True
    tool.interact.selected = [(1.5, 3.5), (300.5, 550)]
    tool.interact.brushing = False

    roi = data_image.subsets[0].subset_state.roi
    assert isinstance(roi, EllipticalROI)
    assert_allclose(roi.xc, 151.00)
    assert_allclose(roi.yc, 276.75)
    assert_allclose(roi.radius_x, 149.5)
    assert_allclose(roi.radius_y, 273.25)


def test_imshow_equal_aspect(app, data_image):
    data = Data(array=np.random.random((100, 5)))
    app.data_collection.append(data)
    v = app.imshow(data=data)
    # Since the widget isn't actually shown during the testing we set the axes
    # ratio manually here
    v.state._set_axes_aspect_ratio(1)
    v.state.reset_limits()
    assert v.state.aspect == 'equal'
    assert v.scale_x.min == -48.0
    assert v.scale_x.max == +52.0
    assert v.scale_y.min == -0.5
    assert v.scale_y.max == +99.5
    v.state.aspect = 'auto'
    # NOTE: the limits don't actually change automatically, because if user
    # is zoomed in they might not want to automatically zoom all the way out
    # again.
    assert v.scale_x.min == -48.0
    assert v.scale_x.max == +52.0
    assert v.scale_y.min == -0.5
    assert v.scale_y.max == +99.5
    v.state.aspect = 'equal'
    assert v.scale_x.min == -48.0
    assert v.scale_x.max == +52.0
    assert v.scale_y.min == -0.5
    assert v.scale_y.max == +99.5


def test_imshow_nonfloat(app):
    data = app.add_data(data_int=np.array([[1, 2], [2, 3]], dtype=np.uint16))[0]
    app.imshow(data=data)


def test_show_axes(app, dataxyz):
    s = app.scatter2d(x='x', y='y', data=dataxyz)
    assert s.state.show_axes
    assert s.viewer_options.widget_show_axes.value
    margin_initial = s.figure.fig_margin
    s.state.show_axes = False
    assert not s.viewer_options.widget_show_axes.value
    assert s.figure.fig_margin != margin_initial
    s.viewer_options.widget_show_axes.value = True
    assert s.state.show_axes
    assert s.figure.fig_margin == margin_initial


def test_notebook():

    # Run an actual notebook

    with open(os.path.join(DATA, 'bqplot.ipynb')) as f:
        nb = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    ep.preprocess(nb, {'metadata': {'path': DATA}})
