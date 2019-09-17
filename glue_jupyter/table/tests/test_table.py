def test_table(app, dataxyz):
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
