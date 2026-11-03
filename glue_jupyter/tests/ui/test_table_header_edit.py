import pytest
from glue.core import Data

import glue_jupyter as gj
from glue_jupyter.tests.helpers import HAS_VISUAL_TEST_DEPS


def create_table_viewer(page_session, data, renameable=(), removable=()):
    page_session.set_viewport_size({"width": 800, "height": 600})
    app = gj.jglue(data=data)
    viewer = app.table(data=data, show=False)
    viewer.state.renameable_components = [data.id[label] for label in renameable]
    viewer.state.removable_components = [data.id[label] for label in removable]
    viewer.show()
    table = page_session.locator(".glue-data-table")
    table.locator("tbody td").first.wait_for()
    return table


def column_header(table, text):
    return table.locator("thead th", has_text=text)


def header_texts(table):
    # Skip the row number and selection columns
    return [text.strip() for text in table.locator("thead th").all_inner_texts()[2:]]


@pytest.mark.skipif(not HAS_VISUAL_TEST_DEPS, reason="visual test dependencies are not installed")
def test_rename_column(solara_test, page_session):
    data = Data(label='data', x=[1., 2., 3.], y=[10., 20., 30.])
    data.get_component('x').units = 'm'
    table = create_table_viewer(page_session, data, renameable=['x'])

    header = column_header(table, 'x [m]')
    header.hover()
    header.get_by_title("Rename column").click()

    # The input starts with the bare column name rather than the header text,
    # which includes the units, and is focused with the text selected
    edit_input = table.locator("input.glue-header-edit-input")
    assert edit_input.input_value() == 'x'
    page_session.keyboard.type('distance')
    page_session.keyboard.press('Enter')
    page_session.wait_for_timeout(1000)

    assert [c.label for c in data.main_components] == ['distance', 'y']
    assert header_texts(table) == ['distance [m]', 'y']
    assert edit_input.count() == 0

    # The accept icon also renames the column
    header = column_header(table, 'distance [m]')
    header.hover()
    header.get_by_title("Rename column").click()
    edit_input.fill('dist')
    header.get_by_title("Accept (Enter)").click()
    page_session.wait_for_timeout(1000)
    assert header_texts(table) == ['dist [m]', 'y']


@pytest.mark.skipif(not HAS_VISUAL_TEST_DEPS, reason="visual test dependencies are not installed")
def test_rename_column_cancel(solara_test, page_session):
    data = Data(label='data', x=[1., 2., 3.], y=[10., 20., 30.])
    table = create_table_viewer(page_session, data, renameable=['x'])

    header = column_header(table, 'x')
    header.hover()
    header.get_by_title("Rename column").click()
    page_session.keyboard.type('a')
    page_session.keyboard.press('Escape')
    page_session.wait_for_timeout(1000)

    assert [c.label for c in data.main_components] == ['x', 'y']
    assert header_texts(table) == ['x', 'y']
    assert table.locator("input.glue-header-edit-input").count() == 0


@pytest.mark.skipif(not HAS_VISUAL_TEST_DEPS, reason="visual test dependencies are not installed")
def test_rename_column_with_quotes(solara_test, page_session):
    data = Data(label='data', y=[10., 20., 30.])
    data.add_component([1., 2., 3.], 'say "hi"')
    table = create_table_viewer(page_session, data, renameable=['say "hi"'])

    # The rename input is found with a selector built from the column name, so
    # quotes in the name must not stop it from being focused
    header = column_header(table, 'say "hi"')
    header.hover()
    header.get_by_title("Rename column").click()
    page_session.wait_for_timeout(500)
    page_session.keyboard.type('greeting')
    page_session.keyboard.press('Enter')
    page_session.wait_for_timeout(1000)

    assert header_texts(table) == ['y', 'greeting']


@pytest.mark.skipif(not HAS_VISUAL_TEST_DEPS, reason="visual test dependencies are not installed")
def test_remove_column(solara_test, page_session):
    data = Data(label='data', x=[1., 2., 3.], y=[10., 20., 30.])
    table = create_table_viewer(page_session, data, removable=['x'])

    # Cancelling the confirmation keeps the column
    header = column_header(table, 'x')
    header.hover()
    header.get_by_title("Delete column").click()
    assert header.get_by_text("remove 'x'?").is_visible()
    header.get_by_title("Cancel").click()
    page_session.wait_for_timeout(1000)
    assert header_texts(table) == ['x', 'y']

    # Confirming it removes the column from the data
    header.hover()
    header.get_by_title("Delete column").click()
    header.get_by_title("Confirm delete").click()
    page_session.wait_for_timeout(1000)
    assert [c.label for c in data.main_components] == ['y']
    assert header_texts(table) == ['y']


@pytest.mark.skipif(not HAS_VISUAL_TEST_DEPS, reason="visual test dependencies are not installed")
def test_header_controls_opt_in(solara_test, page_session):
    data = Data(label='data', x=[1., 2., 3.], y=[10., 20., 30.])
    table = create_table_viewer(page_session, data, renameable=['x'], removable=['x'])

    # The controls only appear on hover, and only for columns that opted in
    header_x = column_header(table, 'x')
    header_y = column_header(table, 'y')
    assert not header_x.get_by_title("Rename column").is_visible()
    assert not header_x.get_by_title("Delete column").is_visible()
    header_x.hover()
    assert header_x.get_by_title("Rename column").is_visible()
    assert header_x.get_by_title("Delete column").is_visible()
    header_y.hover()
    assert not header_x.get_by_title("Rename column").is_visible()
    assert header_y.get_by_title("Rename column").count() == 0
    assert header_y.get_by_title("Delete column").count() == 0


@pytest.mark.skipif(not HAS_VISUAL_TEST_DEPS, reason="visual test dependencies are not installed")
def test_header_controls_do_not_change_column_widths(solara_test, page_session):
    data = Data(label='data', x=[1., 2., 3.], y=[10., 20., 30.])
    table = create_table_viewer(page_session, data, renameable=['x'], removable=['x'])

    def widths():
        return [header.bounding_box()['width'] for header in table.locator("thead th").all()]

    # Showing the controls on hover should not make the columns jump around
    initial = widths()
    column_header(table, 'x').hover()
    page_session.wait_for_timeout(500)
    assert widths() == pytest.approx(initial, abs=0.5)
    column_header(table, 'y').hover()
    page_session.wait_for_timeout(500)
    assert widths() == pytest.approx(initial, abs=0.5)
