import numpy as np

from glue_jupyter import jglue
from glue_jupyter.tests.helpers import visual_widget_test


@visual_widget_test
def test_visual_incompatible_subset(
    tmp_path,
    page_session,
    solara_test,
):

    # Regression test for a bug that caused incompatible subsets
    # to make the whole image green.

    np.random.seed(12345)
    im = np.random.random((64, 64))
    x = np.random.normal(3, 1, 100)
    y = np.random.normal(2, 1.5, 100)

    app = jglue()
    data1 = app.add_data(image={"image": im})[0]
    data2 = app.add_data(catalog={"x": x, "y": y})[0]
    image = app.imshow(data=data1, show=False)
    state1 = data1.pixel_component_ids[1] > 32
    app.data_collection.new_subset_group('image[x] > 32', state1)
    state2 = data2.id['x'] > 1
    app.data_collection.new_subset_group('x > 1', state2)
    figure = image.figure_widget
    figure.layout = {"width": "400px", "height": "250px"}
    return figure
