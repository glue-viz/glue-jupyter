import numpy as np
import pytest
from glue.core import Data
from IPython.display import display

import glue_jupyter as gj
from glue_jupyter.tests.helpers import HAS_VISUAL_TEST_DEPS

pytestmark = pytest.mark.skipif(not HAS_VISUAL_TEST_DEPS, reason="requires solara, playwright")


@pytest.fixture
def viewer_and_page(solara_test, page_session):
    data = Data(x=np.arange(1000).reshape((10, 10, 10)), label="cube")
    app = gj.jglue(cube=data)
    viewer = app.imshow(data=data, show=False)
    page_session.set_viewport_size({"width": 800, "height": 600})
    return app, viewer, page_session


def test_slice_slider(viewer_and_page):
    """Test that clicking the slice slider updates viewer state."""
    _app, viewer, page = viewer_and_page

    widget = viewer.viewer_options
    assert len(widget.sliders) == 1
    initial_slice = viewer.state.slices[0]

    display(widget)
    slider = page.locator(".glue-viewer-image .v-slider")
    slider.wait_for()
    page.wait_for_timeout(500)

    # Click near the right end of the slider track
    box = slider.bounding_box()
    page.mouse.click(box["x"] + box["width"] * 0.9, box["y"] + box["height"] / 2)
    page.wait_for_timeout(500)

    assert viewer.state.slices[0] > initial_slice


def test_colormap(viewer_and_page):
    """Test that changing the colormap via the UI updates layer state."""
    _app, viewer, page = viewer_and_page

    layer_panel = viewer._layout_layer_options.layers[0]['layer_panel']
    original_cmap = layer_panel.layer_state.cmap.name

    display(layer_panel)
    page.wait_for_timeout(500)

    # Open the colormap dropdown and pick a different colormap
    cmap_select = page.locator(".v-select").filter(has_text="colormap").first
    cmap_select.click()
    page.wait_for_timeout(300)

    # Pick a colormap that isn't the current one
    target = "viridis" if original_cmap != "viridis" else "plasma"
    page.locator(f".v-list-item:has-text('{target}')").first.click()
    page.wait_for_timeout(300)

    assert layer_panel.layer_state.cmap.name == target
    assert layer_panel.layer_state.cmap.name != original_cmap
