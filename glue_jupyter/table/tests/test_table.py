from glue_jupyter.table import TableViewer


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
