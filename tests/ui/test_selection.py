import pytest
import glue_jupyter as gj
import numpy as np
from glue.core.edit_subset_mode import ReplaceMode


selection_width = 200
selection_height = 40


@pytest.mark.parametrize("compression", ["png"])
def test_elliptical_selection(solara_test, page_session, assert_solara_snapshot, compression, request):
    app, viewer, plot = create_viewer(page_session)

    # click elliptical selection tool
    page_session.mouse.move(240, 31)
    page_session.mouse.down()
    page_session.mouse.up()
    page_session.wait_for_timeout(100)

    center_x, center_y = center_of_element(page_session, ".bqplot")

    # mouse down on center of plot
    page_session.mouse.move(center_x, center_y)
    page_session.mouse.down()
    page_session.wait_for_timeout(100)

    # move right and down and release mouse
    page_session.mouse.move(center_x + selection_width / 2, center_y + selection_height / 2)
    page_session.mouse.up()
    page_session.wait_for_timeout(100)
    page_session.pause()
    assert_solara_snapshot(plot.screenshot())


@pytest.mark.parametrize("compression", ["png"])
def test_elliptical_selection_rotate(solara_test, page_session, assert_solara_snapshot, compression, request):
    app, viewer, plot = create_viewer(page_session)

    # click elliptical selection tool
    page_session.mouse.move(240, 31)
    page_session.mouse.down()
    page_session.mouse.up()
    page_session.wait_for_timeout(100)

    center_x, center_y = center_of_element(page_session, ".bqplot")

    # mouse down on center of plot
    page_session.mouse.move(center_x, center_y)
    page_session.mouse.down()
    page_session.wait_for_timeout(100)

    # move right and down and release mouse
    page_session.mouse.move(center_x + selection_width / 2, center_y + selection_height / 2)
    page_session.mouse.up()
    page_session.wait_for_timeout(100)

    rotate(45, app, viewer)
    page_session.wait_for_timeout(100)

    assert_solara_snapshot(plot.screenshot())


@pytest.mark.parametrize("compression", ["png"])
def test_rectangular_selection(solara_test, page_session, assert_solara_snapshot, compression, request):
    app, viewer, plot = create_viewer(page_session)

    # click rectangular selection tool
    page_session.mouse.move(135, 31)
    page_session.mouse.down()
    page_session.mouse.up()
    page_session.wait_for_timeout(100)

    center_x, center_y = center_of_element(page_session, ".bqplot")

    # mouse down on center of plot
    page_session.mouse.move(center_x - selection_width / 2, center_y - selection_height / 2)
    page_session.mouse.down()
    page_session.wait_for_timeout(100)

    # move right and down and release mouse
    page_session.mouse.move(center_x + selection_width / 2, center_y + selection_height / 2)
    page_session.mouse.up()
    page_session.wait_for_timeout(100)

    assert_solara_snapshot(plot.screenshot())


@pytest.mark.parametrize("compression", ["png"])
def test_rectangular_selection_rotate(solara_test, page_session, assert_solara_snapshot, compression, request):
    app, viewer, plot = create_viewer(page_session)

    # click rectangular selection tool
    page_session.mouse.move(135, 31)
    page_session.mouse.down()
    page_session.mouse.up()
    page_session.wait_for_timeout(100)

    center_x, center_y = center_of_element(page_session, ".bqplot")

    # mouse down on center of plot
    page_session.mouse.move(center_x - selection_width / 2, center_y - selection_height / 2)
    page_session.mouse.down()
    page_session.wait_for_timeout(100)

    # move right and down and release mouse
    page_session.mouse.move(center_x + selection_width / 2, center_y + selection_height / 2)
    page_session.mouse.up()
    page_session.wait_for_timeout(100)

    rotate(45, app, viewer)
    page_session.wait_for_timeout(100)

    assert_solara_snapshot(plot.screenshot())


def create_viewer(page_session):
    page_session.set_viewport_size({ "width": 500, "height": 600 })
    points = gj.example_data_xyz(loc=0, scale=1, N=10*1000)
    app = gj.jglue(points=points)
    viewer = app.scatter2d(x='x', y='y', show=False)
    viewer.figure_widget.layout.width = '500px'
    viewer.figure_widget.layout.height = '500px'
    viewer.state.show_axes = False
    viewer.figure_widget.fig_margin = dict(left=0, right=0, top=0, bottom=0)
    viewer.show()

    plot = page_session.locator(".jp-OutputArea-output")
    plot.wait_for()
    page_session.wait_for_timeout(100)
    return app, viewer, plot

def center_of_element(page_session, selector):
    """
    Returns the center coordinates of a given element on the page.
    """
    bounding_box = page_session.query_selector(selector).bounding_box()
    center_x = bounding_box["x"] + bounding_box["width"] / 2
    center_y = bounding_box["y"] + bounding_box["height"] / 2
    return center_x, center_y


def rotate(angle, app, viewer):
    subset_to_update = app.session.data_collection.subset_groups[0]
    subset_to_update.subset_state.roi.theta = np.radians(angle)
    app.session.edit_subset_mode._combine_data(subset_to_update.subset_state, override_mode=ReplaceMode)
    tool = viewer.toolbar.active_tool
    tool.update_from_roi(subset_to_update.subset_state.roi)
