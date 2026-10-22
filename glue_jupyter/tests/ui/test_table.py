import pytest
from glue.core import Data

import glue_jupyter as gj
from glue_jupyter.tests.helpers import HAS_VISUAL_TEST_DEPS


def create_table_viewer(page_session):
    page_session.set_viewport_size({"width": 800, "height": 600})
    data = Data(label='data', x=[3, 1, 2], y=[30, 10, 20])
    app = gj.jglue(data=data)
    viewer = app.table(data=data, show=False)
    viewer.show()
    table = page_session.locator(".glue-data-table")
    table.wait_for()
    table.locator("tbody td").first.wait_for()
    return app, viewer, table


def column_texts(table, column):
    return [cell.inner_text() for cell in table.locator(f"tbody tr td:nth-child({column})").all()]


@pytest.mark.skipif(not HAS_VISUAL_TEST_DEPS, reason="visual test dependencies are not installed")
def test_table_headers(solara_test, page_session):
    _app, _viewer, table = create_table_viewer(page_session)
    headers = table.locator("thead th")
    assert headers.all_inner_texts() == ['#', '', 'x', 'y']
    assert column_texts(table, 3) == ['3', '1', '2']

    # Clicking a column header sorts ascending, descending, then clears the sort
    header_x = headers.nth(2)
    header_x.click()
    page_session.wait_for_timeout(500)
    assert column_texts(table, 3) == ['1', '2', '3']
    header_x.click()
    page_session.wait_for_timeout(500)
    assert column_texts(table, 3) == ['3', '2', '1']
    header_x.click()
    page_session.wait_for_timeout(500)
    assert column_texts(table, 3) == ['3', '1', '2']
