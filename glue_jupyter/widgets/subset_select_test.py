def test_subset_select(app, datax, dataxyz, dataxz):
    subset_select = app.widget_subset_select

    assert len(subset_select.available) == 0
    assert len(app.data_collection.subset_groups) == 0
    assert subset_select.selected == []

    # if there are no subsets, you cannot select multiple
    assert subset_select.available == []
    assert not subset_select.multiple
    assert subset_select.selected == []

    # now we make a selection
    app.subset_lasso2d(dataxyz.id['x'], dataxyz.id['y'], [0.5, 2.5, 2.5, 0.5], [1, 1, 3.5, 3.5])

    assert len(subset_select.available) == 1
    assert subset_select.available[0]['label'] == 'Subset 1'

    assert subset_select.selected[0] == 0

    app.session.edit_subset_mode.edit_subset = [app.data_collection.subset_groups[0]]
    assert subset_select.selected[0] == 0

    # glue -> ui
    # we select no subsets, should go back to new subset
    app.session.edit_subset_mode.edit_subset = []
    assert subset_select.selected == []

    # ui -> glue
    subset_select.selected = [0]
    assert app.session.edit_subset_mode.edit_subset == [app.data_collection.subset_groups[0]]

    # glue -> ui (reset again)
    app.session.edit_subset_mode.edit_subset = []
    assert subset_select.selected == []
    assert dataxyz.subsets[0]['x'].tolist() == [1, 2]
    assert dataxyz.subsets[0]['y'].tolist() == [2, 3]
    assert dataxyz.subsets[0]['z'].tolist() == [5, 6]

    # now do a second selection
    app.session.edit_subset_mode.edit_subset = [app.data_collection.subset_groups[0]]
    assert subset_select.selected == [0]

    app.session.edit_subset_mode.edit_subset = []
    assert subset_select.selected == []

    app.subset_lasso2d(dataxyz.id['x'], dataxyz.id['y'], [0.5, 2.5, 2.5, 0.5], [1, 1, 3.5, 3.5])
    assert len(subset_select.available) == 2
    assert subset_select.available[1]['label'] == 'Subset 2'
    assert subset_select.selected == [1]

    # we do not have multiple subsets enabled
    subset_select.selected = [0]

    # do multiple
    subset_select.multiple = True
    # now nothing should have changed in the selected subsets
    subset_select.selected = [0, 1]
    assert len(app.session.edit_subset_mode.edit_subset) == 2
    subset_select.selected = [0]
    assert len(app.session.edit_subset_mode.edit_subset) == 1

    # select multiple, then set multiple to false
    subset_select.selected = [0, 1]
    assert len(app.session.edit_subset_mode.edit_subset) == 2
    subset_select.multiple = False
    assert subset_select.selected == [0]
    assert len(app.session.edit_subset_mode.edit_subset) == 1

    # switch multiple on again
    subset_select.multiple = True
    assert subset_select.selected == [0]

    # and check again, now second selected
    subset_select.selected = [1]
    subset_select.multiple = False

    # if we deselect all, we should go to the 'new' state
    subset_select.selected = []
