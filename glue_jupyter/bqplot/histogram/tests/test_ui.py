import numpy as np
import pytest
from glue.core import Data
from IPython.display import display

import glue_jupyter as gj
from glue_jupyter.tests.helpers import HAS_VISUAL_TEST_DEPS

pytestmark = pytest.mark.skipif(not HAS_VISUAL_TEST_DEPS, reason="requires solara, playwright")


@pytest.fixture
def viewer_and_page(solara_test, page_session):
    data = Data(x=np.random.RandomState(42).uniform(0, 10, 1000), label="data")
    app = gj.jglue(data=data)
    viewer = app.histogram1d(x='x', show=False)
    page_session.set_viewport_size({"width": 800, "height": 600})
    return app, viewer, page_session


def _click_switch(page, label):
    switch = page.locator(f".v-input--switch:has(.v-label:text('{label}'))")
    switch.click()
    page.wait_for_timeout(300)


def test_normalize_and_cumulative(viewer_and_page):
    """Test that the normalize and cumulative switches update viewer state."""
    _app, viewer, page = viewer_and_page

    display(viewer.viewer_options)
    page.wait_for_timeout(500)

    assert not viewer.state.normalize
    assert not viewer.state.cumulative

    _click_switch(page, "Normalize")
    assert viewer.state.normalize

    _click_switch(page, "Cumulative")
    assert viewer.state.cumulative

    # Toggle them back off
    _click_switch(page, "Normalize")
    assert not viewer.state.normalize

    _click_switch(page, "Cumulative")
    assert not viewer.state.cumulative


def test_fit_bins_to_axes(viewer_and_page):
    """Test that updating x-min/x-max then clicking Fit Bins to Axes works."""
    _app, viewer, page = viewer_and_page

    display(viewer.viewer_options)
    page.wait_for_timeout(500)

    # Set non-default x range via the state and verify the UI will pick it up
    viewer.state.x_min = 2.0
    viewer.state.x_max = 8.0
    page.wait_for_timeout(300)

    original_hist_x_min = viewer.state.hist_x_min
    original_hist_x_max = viewer.state.hist_x_max

    # Click the "Fit Bins to Axes" button
    page.locator("button:has-text('Fit Bins to Axes')").click()
    page.wait_for_timeout(300)

    assert viewer.state.hist_x_min == pytest.approx(2.0)
    assert viewer.state.hist_x_max == pytest.approx(8.0)
    assert viewer.state.hist_x_min != original_hist_x_min
    assert viewer.state.hist_x_max != original_hist_x_max
