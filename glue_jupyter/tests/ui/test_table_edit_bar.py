import pytest
from glue.core import Data

import glue_jupyter as gj
from glue_jupyter.tests.helpers import HAS_VISUAL_TEST_DEPS


@pytest.mark.skipif(not HAS_VISUAL_TEST_DEPS, reason="visual test dependencies are not installed")
def test_edit_bar_follows_programmatic_changes(solara_test, page_session):
    page_session.set_viewport_size({"width": 800, "height": 600})
    data = Data(label='data', x=[1., 2., 3.], y=[10., 20., 30.])
    app = gj.jglue(data=data)
    viewer = app.table(data=data, show=False)
    viewer.state.editable_components = [data.id['x']]
    viewer.show()
    table = page_session.locator(".glue-data-table")
    table.locator("tbody td").first.wait_for()

    edit_input = page_session.locator(".edit-bar-input input")

    # Select the x cell in the first row
    table.locator("tbody tr").first.locator("td.glue-selectable-cell").first.click()
    page_session.wait_for_timeout(500)
    assert edit_input.input_value() == '1'

    # Changing the column programmatically should refresh the edit bar
    data.update_components({data.id['x']: [5., 6., 7.]})
    page_session.wait_for_timeout(1000)
    assert edit_input.input_value() == '5'

    # ... unless the user has started typing a new value
    edit_input.fill('42')
    data.update_components({data.id['x']: [8., 9., 10.]})
    page_session.wait_for_timeout(1000)
    assert edit_input.input_value() == '42'

    # Committing the typed value updates the data and moves to the next row
    edit_input.press('Enter')
    page_session.wait_for_timeout(1000)
    assert list(data['x']) == [42., 9., 10.]
    assert edit_input.input_value() == '9'
