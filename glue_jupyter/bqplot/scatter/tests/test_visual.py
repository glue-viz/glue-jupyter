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
    return scatter._layout
