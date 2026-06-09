import numpy as np
import pytest

from glue_jupyter import jglue
from glue_jupyter.tests.helpers import visual_widget_test


@pytest.mark.parametrize(("x_log", "y_log"), [
    (False, False),
    (True, False),
    (False, True),
    (True, True),
], ids=["linear", "xlog", "ylog", "xylog"])
@visual_widget_test
def test_visual_histogram1d_log(
    tmp_path,
    page_session,
    solara_test,
    x_log,
    y_log,
):

    np.random.seed(12345)

    x = np.random.lognormal(2, 0.7, 5000)

    app = jglue()
    data = app.add_data(a={"x": x})[0]
    histogram = app.histogram1d(show=False, data=data)

    app.data_collection.new_subset_group(
        subset_state=data.id['x'] > np.median(x),
        label='right half',
    )

    histogram.state.x_log = x_log
    histogram.state.y_log = y_log

    figure = histogram.figure_widget
    figure.layout = {"width": "400px", "height": "250px"}
    return figure
