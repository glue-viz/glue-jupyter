import numpy as np
from numpy.testing import assert_allclose

from glue_jupyter import jglue
from glue_jupyter.tests.helpers import visual_widget_test


@visual_widget_test
def test_contour_units(
    tmp_path,
    page_session,
    solara_test,
):

    x = np.linspace(-7, 7, 88)
    y = np.linspace(-6, 6, 69)
    X, Y = np.meshgrid(x, y)
    Z = np.exp(-(X * X + Y * Y) / 4)

    app = jglue()
    data = app.add_data(data={"x": X, "y": Y, "z": Z})[0]
    data.get_component("z").units = 'km'
    image = app.imshow(show=False)
    image.state.layers[0].attribute = data.id['z']
    image.state.layers[0].contour_visible = True
    image.state.layers[0].c_min = 0.1
    image.state.layers[0].c_max = 0.9
    image.state.layers[0].n_levels = 5

    assert_allclose(image.state.layers[0].levels, [0.1, 0.3, 0.5, 0.7, 0.9])

    image.state.layers[0].attribute_display_unit = 'mm'
    image.state.layers[0].attribute_display_unit = 'km'
    image.state.layers[0].attribute_display_unit = 'm'

    assert_allclose(image.state.layers[0].levels, [100, 300, 500, 700, 900])
    assert image.state.layers[0].labels == ['100', '300', '500', '700', '900']

    figure = image.figure_widget
    figure.layout = {"width": "400px", "height": "250px"}
    return figure
