import numpy as np
from glue.core import Data

from glue_jupyter.table import TableViewer


def test_table_sort(app, dataxyz):
    table = app.table(data=dataxyz)

    # Initially unsorted - items should be in original order
    items = table.widget_table.items
    assert [item['x'] for item in items] == [1, 2, 3]
    assert [item['__row__'] for item in items] == [0, 1, 2]

    # Sort ascending by x
    table.widget_table.vue_sort_column('x')
    items = table.widget_table.items
    assert [item['x'] for item in items] == [1, 2, 3]
    assert [item['__row__'] for item in items] == [0, 1, 2]

    # Sort descending by x
    table.widget_table.vue_sort_column('x')
    items = table.widget_table.items
    assert [item['x'] for item in items] == [3, 2, 1]
    assert [item['__row__'] for item in items] == [2, 1, 0]

    # Clear sort
    table.widget_table.vue_sort_column('x')
    items = table.widget_table.items
    assert [item['x'] for item in items] == [1, 2, 3]
    assert [item['__row__'] for item in items] == [0, 1, 2]


def test_table_sort_selection(app):
    # Create data where sorting will reorder rows
    data = Data(x=[3, 1, 2], y=[30, 10, 20], label="unsorted data")
    app.add_data(data)
    table = app.table(data=data)

    # Sort ascending by x (will reorder to indices [1, 2, 0])
    table.widget_table.vue_sort_column('x')
    items = table.widget_table.items
    assert [item['x'] for item in items] == [1, 2, 3]
    assert [item['__row__'] for item in items] == [1, 2, 0]

    # Select the first row in the sorted view (which is original index 1)
    table.widget_table.checked = [1]
    table.apply_filter()

    # Verify subset was created with correct original index
    assert len(table.layers) == 2
    subset = table.layers[1].layer
    mask = subset.to_mask()
    assert list(mask) == [False, True, False]  # Only original index 1 selected

    # Select multiple rows in sorted view
    table.widget_table.checked = [1, 0]  # Original indices 1 and 0
    table.apply_filter()

    # The subset should contain original indices 0 and 1
    mask = subset.to_mask()
    assert list(mask) == [True, True, False]


def test_table_sort_pagination(app):
    # Create larger dataset to test pagination with sorting
    data = Data(x=np.array([5, 2, 8, 1, 9, 3, 7, 4, 6, 0, 11, 10]),
                label="pagination data")
    app.add_data(data)
    table = app.table(data=data)

    # Set page size to 5
    table.widget_table.options = {**table.widget_table.options, 'itemsPerPage': 5}

    # Sort ascending
    table.widget_table.vue_sort_column('x')
    items = table.widget_table.items
    # First page should have smallest 5 values
    assert [item['x'] for item in items] == [0, 1, 2, 3, 4]
    # __row__ should be original indices
    assert [item['__row__'] for item in items] == [9, 3, 1, 5, 7]

    # Go to page 2
    table.widget_table.options = {**table.widget_table.options, 'page': 2}
    items = table.widget_table.items
    assert [item['x'] for item in items] == [5, 6, 7, 8, 9]
    assert [item['__row__'] for item in items] == [0, 8, 6, 2, 4]


def test_table_column_visibility_widget(app, dataxyz):
    table = app.table(data=dataxyz)
    options_widget = table._layout_viewer_options

    # Check that all columns are listed and visible by default
    column_names = [item['text'] for item in options_widget.column_items]
    assert 'x' in column_names
    assert 'y' in column_names
    assert 'z' in column_names
    assert set(options_widget.visible_columns) == set(column_names)

    # Hide a column via the widget
    options_widget.visible_columns = ['x', 'z']

    # Check that hidden_components is updated
    hidden_names = [str(c) for c in table.state.hidden_components]
    assert 'y' in hidden_names
    assert 'x' not in hidden_names
    assert 'z' not in hidden_names

    # Check the table headers are updated
    header_names = [h['text'] for h in table.widget_table.headers]
    assert 'x' in header_names
    assert 'z' in header_names
    assert 'y' not in header_names

    # Hide a column via state and check widget updates
    table.state.hidden_components = [dataxyz.id['x'], dataxyz.id['z']]
    assert 'x' not in options_widget.visible_columns
    assert 'z' not in options_widget.visible_columns
    assert 'y' in options_widget.visible_columns


def test_table_filter(app, dataxyz):
    table = app.table(data=dataxyz)
    assert len(table.layers) == 1
    assert table.widget_table is not None
    table.widget_table.checked = [1]
    table.apply_filter()
    assert len(table.layers) == 2
    subset = table.layers[1].layer
    assert table.widget_table.selections == [subset.label]
    assert [k['text'] for k in table.widget_table.headers_selections] == [subset.label]
    assert table.widget_table.selection_colors == [subset.style.color]

    app.subset('test', dataxyz.id['x'] > 1)
    assert len(table.layers) == 3
    assert len(table.widget_table.selections) == 2


def test_table_remove_subset_group(app, dataxyz):
    table = app.table(data=dataxyz)
    assert len(table.layers) == 1
    assert len(table.widget_table.selections) == 0

    # Create two subset groups
    app.subset('subset1', dataxyz.id['x'] > 1)
    app.subset('subset2', dataxyz.id['y'] > 2)
    assert len(table.layers) == 3
    assert len(table.widget_table.selections) == 2
    assert 'subset1' in table.widget_table.selections
    assert 'subset2' in table.widget_table.selections

    # Remove the second subset group
    app.data_collection.remove_subset_group(app.data_collection.subset_groups[1])
    assert len(table.layers) == 2
    assert len(table.widget_table.selections) == 1
    assert 'subset1' in table.widget_table.selections
    assert 'subset2' not in table.widget_table.selections

    # Remove the first subset group
    app.data_collection.remove_subset_group(app.data_collection.subset_groups[0])
    assert len(table.layers) == 1
    assert len(table.widget_table.selections) == 0


def test_table_add_remove_data(app, dataxyz, dataxz, data_empty):
    table = app.new_data_viewer(TableViewer, data=None, show=True)
    assert len(table.layers) == 0
    assert table.widget_table.total_length == 0

    app.add_data(data_empty)
    table.add_data(data_empty)
    assert len(table.layers) == 1
    assert table.widget_table.total_length == 0
    table.remove_data(data_empty)

    table.add_data(dataxyz)
    assert table.widget_table.data is dataxyz
    assert table.widget_table.total_length == 3

    assert table.widget_table.items, "table should fill automatically"
    assert table.widget_table.items[0]['z'] == dataxyz['z'][0]
    assert table.widget_table.total_length, "total length should grow"

    assert dataxz['z'][0] != dataxyz['z'][0], "we assume this to check data changes in the table"

    table.add_data(dataxz)
    assert table.widget_table.data is dataxz
    assert table.widget_table.items[0]['z'] == dataxz['z'][0]
    assert len(table.layers) == 2

    table.remove_data(dataxz)
    assert table.widget_table.data is dataxyz
    assert table.widget_table.items[0]['z'] == dataxyz['z'][0]
    assert len(table.layers) == 1

    table.remove_data(dataxyz)
    assert table.widget_table.data is None
    assert table.widget_table.items == []
    assert len(table.layers) == 0
