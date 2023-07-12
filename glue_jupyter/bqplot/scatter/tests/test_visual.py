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
