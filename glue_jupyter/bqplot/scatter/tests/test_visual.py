import pytest

import numpy as np
import matplotlib.pyplot as plt

from glue_jupyter import jglue
from glue_jupyter.tests.helpers import visual_widget_test


@visual_widget_test
def test_visual_scatter2d(
    tmp_path,
    page_session,
    solara_test,
):

    np.random.seed(12345)
    x = np.random.normal(3, 1, 1000)
    y = np.random.normal(2, 1.5, 1000)
    c = np.hypot(x - 3, y - 2)
    s = (x - 3)

    app = jglue()
    data = app.add_data(a={"x": x, "y": y, "c": c, "s": s})[0]
    scatter = app.scatter2d(show=False)
    scatter.state.layers[0].cmap_mode = 'Linear'
    scatter.state.layers[0].cmap_att = data.id['c']
    scatter.state.layers[0].cmap = plt.cm.viridis
    scatter.state.layers[0].size_mode = 'Linear'
    scatter.state.layers[0].size_att = data.id['s']
    figure = scatter.figure_widget
    figure.layout = {"width": "400px", "height": "250px"}
    return figure


@visual_widget_test
def test_visual_scatter2d_density(
    tmp_path,
    page_session,
    solara_test,
):

    # Test that for many points, density maps are shown

    np.random.seed(12345)

    app = jglue()

    x = np.random.normal(3, 1, 100)
    y = np.random.normal(2, 1.5, 100)
    c = np.hypot(x - 3, y - 2)
    s = (x - 3)

    data1 = app.add_data(a={"x": x, "y": y, "c": c, "s": s})[0]

    xx = np.random.normal(3, 1, 1000000)
    yy = np.random.normal(2, 1.5, 1000000)

    data2 = app.add_data(a={"x": xx, "y": yy})[0]

    app.add_link(data1, 'x', data2, 'x')
    app.add_link(data1, 'y', data2, 'y')

    scatter = app.scatter2d(show=False, data=data1)
    scatter.add_data(data2)

    scatter.state.layers[0].cmap_mode = 'Linear'
    scatter.state.layers[0].cmap_att = data1.id['c']
    scatter.state.layers[0].cmap = plt.cm.viridis
    scatter.state.layers[0].size_mode = 'Linear'
    scatter.state.layers[0].size_att = data1.id['s']

    scatter.state.layers[1].zorder = 0.5

    figure = scatter.figure_widget
    figure.layout = {"width": "400px", "height": "250px"}
    return figure


@pytest.mark.xfail
@visual_widget_test
def test_visual_linestyle(
    tmp_path,
    page_session,
    solara_test,
):

    x = np.array([1, 2, 4, 5])
    y = np.array([3, 2, 1, 8])

    app = jglue()

    data_a = app.add_data(a={"x": x, "y": y})[0]
    data_b = app.add_data(b={"x": x, "y": y+1})[0]
    data_c = app.add_data(c={"x": x, "y": y+2})[0]

    app.add_link(data_a, 'x', data_b, 'x')
    app.add_link(data_a, 'x', data_c, 'x')
    app.add_link(data_a, 'y', data_b, 'y')
    app.add_link(data_a, 'y', data_c, 'y')

    scatter = app.scatter2d(show=False, data=data_a)
    scatter.add_data(data_b)
    scatter.add_data(data_c)

    scatter.state.layers[0].line_visible = True
    scatter.state.layers[0].linestyle = 'solid'
    scatter.state.layers[1].line_visible = True
    scatter.state.layers[1].linestyle = 'dashed'
    scatter.state.layers[2].line_visible = True
    scatter.state.layers[2].linestyle = 'dashdot'

    assert scatter.layers[0].line_mark_gl.visible
    assert not scatter.layers[1].line_mark_gl.visible
    assert not scatter.layers[2].line_mark_gl.visible

    figure = scatter.figure_widget
    figure.layout = {"width": "800px", "height": "500px"}
    return figure


@pytest.mark.xfail
@visual_widget_test
def test_visual_vector(
    tmp_path,
    page_session,
    solara_test,
):

    np.random.seed(12345)

    app = jglue()

    datas = []
    for label in 'abc':
        x = np.random.normal(10, 3, 100)
        y = np.random.normal(5, 3, 100)
        theta = np.arctan2(y-5, x - 10)
        vx = -np.sin(theta)
        vy = np.cos(theta)

        data = {}
        data[label] = {"x": x, "y": y, "vx": vx, "vy": vy}
        datas.append(app.add_data(**data)[0])

    for attr in ['x', 'y', 'vx', 'vy']:
        app.add_link(datas[0], attr, datas[1], attr)
        app.add_link(datas[0], attr, datas[2], attr)

    scatter = app.scatter2d(show=False, data=datas[0])
    scatter.add_data(datas[1])
    scatter.add_data(datas[2])

    for index in range(3):
        scatter.state.layers[index].vector_visible = True
        scatter.state.layers[index].vx_att = datas[index].id['vx']
        scatter.state.layers[index].vy_att = datas[index].id['vy']

    scatter.state.layers[1].vector_origin = 'tip'
    scatter.state.layers[2].vector_origin = 'tail'

    scatter.state.layers[0].color = 'red'
    scatter.state.layers[1].color = 'green'
    scatter.state.layers[2].color = 'blue'

    figure = scatter.figure_widget
    figure.layout = {"width": "800px", "height": "500px"}
    return figure
