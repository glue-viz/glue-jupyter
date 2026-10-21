import pytest
from glue.core import Data

import glue_jupyter as gj
from glue_jupyter.tests.helpers import HAS_VISUAL_TEST_DEPS


@pytest.mark.skipif(not HAS_VISUAL_TEST_DEPS, reason="visual test dependencies are not installed")
def test_column_display_units(solara_test, page_session):
    page_session.set_viewport_size({"width": 800, "height": 600})
    data = Data(label='data', x=[1000., 2000., 3000.], y=[1., 2., 3.])
    data.get_component(data.id['x']).units = 'm'
    app = gj.jglue(data=data)
    viewer = app.table(data=data, show=False)
    viewer.state.editable_components = [data.id['x']]
    viewer.show()
    table = page_session.locator(".glue-data-table")
    table.locator("tbody td").first.wait_for()

    def column(index):
        return [cell.inner_text() for cell in table.locator(f"tbody tr td:nth-child({index})").all()]

    assert column(3) == ['1000', '2000', '3000']
    assert [header['text'] for header in viewer.widget_table.headers] == ['x [m]', 'y']

    viewer.state.column_display_units = {'x': 'km'}
    page_session.wait_for_timeout(1000)
    assert column(3) == ['1', '2', '3']
    assert [header['text'] for header in viewer.widget_table.headers] == ['x [km]', 'y']

    # Edits are interpreted in display units
    table.locator("tbody tr").first.locator("td.glue-selectable-cell").first.click()
    edit_input = page_session.locator(".edit-bar-input input")
    page_session.wait_for_timeout(500)
    assert edit_input.input_value() == '1'
    edit_input.fill('5')
    edit_input.press('Enter')
    page_session.wait_for_timeout(1000)
    assert list(data['x']) == [5000., 2000., 3000.]
    assert column(3) == ['5', '2', '3']
