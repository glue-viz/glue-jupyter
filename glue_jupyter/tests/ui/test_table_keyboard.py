import pytest
from glue.core import Data

import glue_jupyter as gj
from glue_jupyter.tests.helpers import HAS_VISUAL_TEST_DEPS


def create_table_viewer(page_session, editable=False):
    page_session.set_viewport_size({"width": 800, "height": 600})
    data = Data(label='data', x=[3., 1., 2.], y=[30., 10., 20.])
    app = gj.jglue(data=data)
    viewer = app.table(data=data, show=False)
    if editable:
        viewer.state.editable_components = [data.id['x']]
    viewer.show()
    table = page_session.locator(".glue-data-table")
    table.locator("tbody td").first.wait_for()
    return data, table


def click_cell(page_session, table, row, column):
    table.locator("tbody tr").nth(row).locator("td.glue-selectable-cell").nth(column).click()
    page_session.wait_for_timeout(500)


def press(page_session, key):
    page_session.keyboard.press(key)
    page_session.wait_for_timeout(500)


@pytest.mark.skipif(not HAS_VISUAL_TEST_DEPS, reason="visual test dependencies are not installed")
def test_keyboard_navigation_read_only(solara_test, page_session):
    errors = []
    page_session.on("pageerror", lambda error: errors.append(error))
    _data, table = create_table_viewer(page_session)
    edit_input = page_session.locator(".edit-bar-input input")
    edit_label = page_session.locator(".edit-bar-label")

    # Clicking a read-only cell focuses the edit bar so that the arrow keys
    # can be used straight away
    click_cell(page_session, table, 0, 0)
    assert edit_label.inner_text() == 'x [0]'
    press(page_session, 'ArrowDown')
    assert edit_label.inner_text() == 'x [1]'
    assert edit_input.input_value() == '1'
    press(page_session, 'Enter')
    assert edit_label.inner_text() == 'x [2]'
    press(page_session, 'ArrowUp')
    assert edit_label.inner_text() == 'x [1]'

    # Navigation stops at the first and last rows
    press(page_session, 'ArrowDown')
    press(page_session, 'ArrowDown')
    assert edit_label.inner_text() == 'x [2]'
    press(page_session, 'Enter')
    assert edit_label.inner_text() == 'x [2]'
    press(page_session, 'ArrowUp')
    press(page_session, 'ArrowUp')
    press(page_session, 'ArrowUp')
    assert edit_label.inner_text() == 'x [0]'

    # Pressing keys with nothing selected should not raise an error
    press(page_session, 'Escape')
    assert edit_label.inner_text() == 'Click a cell to view'
    press(page_session, 'Enter')
    press(page_session, 'ArrowUp')
    assert errors == []

    # With the table sorted, the arrow keys follow the displayed order
    table.locator("thead th").nth(2).click()
    page_session.wait_for_timeout(500)
    click_cell(page_session, table, 0, 0)
    assert edit_label.inner_text() == 'x [1]'
    press(page_session, 'ArrowDown')
    assert edit_label.inner_text() == 'x [2]'
    press(page_session, 'ArrowDown')
    assert edit_label.inner_text() == 'x [0]'


@pytest.mark.skipif(not HAS_VISUAL_TEST_DEPS, reason="visual test dependencies are not installed")
def test_keyboard_navigation_commits_edit(solara_test, page_session):
    data, table = create_table_viewer(page_session, editable=True)
    edit_input = page_session.locator(".edit-bar-input input")
    edit_label = page_session.locator(".edit-bar-label")

    # Moving away from a cell with the arrow keys commits the typed value
    click_cell(page_session, table, 0, 0)
    edit_input.fill('42')
    press(page_session, 'ArrowDown')
    assert list(data['x']) == [42., 1., 2.]
    assert edit_label.inner_text() == 'x [1]'

    # Moving without typing anything leaves the data unchanged
    press(page_session, 'ArrowUp')
    assert edit_label.inner_text() == 'x [0]'
    assert edit_input.input_value() == '42'
    assert list(data['x']) == [42., 1., 2.]

    # Committing on the last row stays on that row
    press(page_session, 'ArrowDown')
    press(page_session, 'ArrowDown')
    edit_input.fill('7')
    press(page_session, 'Enter')
    assert list(data['x']) == [42., 1., 7.]
    assert edit_label.inner_text() == 'x [2]'
    assert edit_input.input_value() == '7'
