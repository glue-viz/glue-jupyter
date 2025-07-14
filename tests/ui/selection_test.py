import pytest
import playwright.sync_api
import glue_jupyter as gj
import numpy as np

@pytest.mark.parametrize("compression", ["png"])
def test_elliptical_selection(solara_test, page_session: playwright.sync_api.Page, assert_solara_snapshot, compression, request):
    page_session.set_viewport_size({ "width": 500, "height": 600 })
    points = gj.example_data_xyz(loc=0, scale=1, N=10*1000)
    app = gj.jglue(points=points)
    app.scatter2d(x='x', y='y')

    plot = page_session.locator(".jp-OutputArea-output")
    plot.wait_for()
    page_session.wait_for_timeout(100)

    # click elliptical selection tool
    page_session.mouse.move(240, 31)
    page_session.mouse.down()
    page_session.mouse.up()
    page_session.wait_for_timeout(100)

    # mouse down on center of plot
    page_session.mouse.move(265, 275)
    page_session.mouse.down()
    page_session.wait_for_timeout(100)

    # move right and down and release mouse
    page_session.mouse.move(365, 290)
    page_session.mouse.up()
    page_session.wait_for_timeout(100)

    assert_solara_snapshot(plot.screenshot())


@pytest.mark.parametrize("compression", ["png"])
def test_elliptical_selection_rotate(solara_test, page_session: playwright.sync_api.Page, assert_solara_snapshot, compression, request):
    page_session.set_viewport_size({ "width": 500, "height": 600 })
    points = gj.example_data_xyz(loc=0, scale=1, N=10*1000)
    app = gj.jglue(points=points)
    app.scatter2d(x='x', y='y')

    plot = page_session.locator(".jp-OutputArea-output")
    plot.wait_for()
    page_session.wait_for_timeout(100)

    # click elliptical selection tool
    page_session.mouse.move(240, 31)
    page_session.mouse.down()
    page_session.mouse.up()
    page_session.wait_for_timeout(100)

    # mouse down on center of plot
    page_session.mouse.move(265, 275)
    page_session.mouse.down()
    page_session.wait_for_timeout(100)

    # move right and down and release mouse
    page_session.mouse.move(365, 290)
    page_session.mouse.up()
    page_session.wait_for_timeout(100)

    from glue.core.edit_subset_mode import ReplaceMode

    subset_to_update = app.session.data_collection.subset_groups[0]
    setattr(subset_to_update.subset_state.roi, "theta", np.radians(45))
    app.session.edit_subset_mode._combine_data(subset_to_update.subset_state, override_mode=ReplaceMode)
    page_session.wait_for_timeout(100)

    assert_solara_snapshot(plot.screenshot())


@pytest.mark.parametrize("compression", ["png"])
def test_rectangular_selection(solara_test, page_session: playwright.sync_api.Page, assert_solara_snapshot, compression, request):
    page_session.set_viewport_size({ "width": 500, "height": 600 })
    points = gj.example_data_xyz(loc=0, scale=1, N=10*1000)
    app = gj.jglue(points=points)
    app.scatter2d(x='x', y='y')

    plot = page_session.locator(".jp-OutputArea-output")
    plot.wait_for()
    page_session.wait_for_timeout(100)

    # click rectangular selection tool
    page_session.mouse.move(135, 31)
    page_session.mouse.down()
    page_session.mouse.up()
    page_session.wait_for_timeout(100)

    # mouse down on center of plot
    page_session.mouse.move(265, 275)
    page_session.mouse.down()
    page_session.wait_for_timeout(100)

    # move right and down and release mouse
    page_session.mouse.move(365, 290)
    page_session.mouse.up()
    page_session.wait_for_timeout(100)

    assert_solara_snapshot(plot.screenshot())


@pytest.mark.parametrize("compression", ["png"])
def test_rectangular_selection_rotate(solara_test, page_session: playwright.sync_api.Page, assert_solara_snapshot, compression, request):
    page_session.set_viewport_size({ "width": 500, "height": 600 })
    points = gj.example_data_xyz(loc=0, scale=1, N=10*1000)
    app = gj.jglue(points=points)
    app.scatter2d(x='x', y='y')

    plot = page_session.locator(".jp-OutputArea-output")
    plot.wait_for()
    page_session.wait_for_timeout(100)

    # click rectangular selection tool
    page_session.mouse.move(135, 31)
    page_session.mouse.down()
    page_session.mouse.up()
    page_session.wait_for_timeout(100)

    # mouse down on center of plot
    page_session.mouse.move(265, 275)
    page_session.mouse.down()
    page_session.wait_for_timeout(100)

    # move right and down and release mouse
    page_session.mouse.move(365, 290)
    page_session.mouse.up()
    page_session.wait_for_timeout(100)

    from glue.core.edit_subset_mode import ReplaceMode

    subset_to_update = app.session.data_collection.subset_groups[0]
    setattr(subset_to_update.subset_state.roi, "theta", np.radians(45))
    app.session.edit_subset_mode._combine_data(subset_to_update.subset_state, override_mode=ReplaceMode)
    page_session.wait_for_timeout(100)

    assert_solara_snapshot(plot.screenshot())
