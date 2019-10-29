def test_subset_select(app, datax, dataxyz, dataxz):
    subset_select = app.widget_subset_select

    assert len(subset_select.widget_menu_items_subsets) == 0
    assert len(app.data_collection.subset_groups) == 0
    assert subset_select.value == "new"

    # if there are no subsets, you cannot select multiple
    assert subset_select.widget_menu_item_select_multiple_checkbox.checked is False
    assert subset_select.widget_menu_item_no_active
    assert not subset_select.widget_menu_item_select_multiple_checkbox.checked
    assert subset_select.value == 'new'

    # now we make a selection
    app.subset_lasso2d(dataxyz.id['x'], dataxyz.id['y'], [0.5, 2.5, 2.5, 0.5], [1, 1, 3.5, 3.5])

    assert len(subset_select.widget_menu_items_subsets) == 1
    assert subset_select.value == 0
    assert subset_select.widget_menu_item_no_active.selected is False

    app.session.edit_subset_mode.edit_subset = [app.data_collection.subset_groups[0]]
    assert subset_select.value == 0
    assert subset_select.widget_menu_item_no_active.selected is False
    assert subset_select.widget_menu_items_subsets[0].selected is True

    # glue -> ui
    # we select no subsets, should go back to new subset
    app.session.edit_subset_mode.edit_subset = []
    assert subset_select.widget_menu_item_no_active.selected is True
    assert subset_select.widget_menu_items_subsets[0].selected is False
    assert subset_select.value == 'new'
    # assert len(subset_select.widgets.index) == 0
    # assert subset_select.widgets.index == ()

    # ui -> glue
    subset_select.value = 0
    assert app.session.edit_subset_mode.edit_subset == [app.data_collection.subset_groups[0]]
    assert subset_select.value == 0
    assert subset_select.widget_menu_item_no_active.selected is False
    assert subset_select.widget_menu_items_subsets[0].selected is True

    # glue -> ui (reset again)
    app.session.edit_subset_mode.edit_subset = []
    assert subset_select.value == 'new'
    assert dataxyz.subsets[0]['x'].tolist() == [1, 2]
    assert dataxyz.subsets[0]['y'].tolist() == [2, 3]
    assert dataxyz.subsets[0]['z'].tolist() == [5, 6]

    # now do a second selection
    app.session.edit_subset_mode.edit_subset = [app.data_collection.subset_groups[0]]
    assert subset_select.widget_menu_items_subsets[0].selected is True
    assert subset_select.widget_menu_item_no_active.selected is False

    subset_select.widget_menu_item_no_active.selected = True
    assert app.session.edit_subset_mode.edit_subset == []
    assert subset_select.widget_menu_items_subsets[0].selected is False

    app.subset_lasso2d(dataxyz.id['x'], dataxyz.id['y'], [0.5, 2.5, 2.5, 0.5], [1, 1, 3.5, 3.5])
    assert subset_select.widget_menu_item_no_active.selected is False
    assert subset_select.widget_menu_items_subsets[0].selected is False
    assert subset_select.widget_menu_items_subsets[1].selected is True
    assert subset_select.value == 1

    # we do not have multiple subsets enabled
    # subset_select.widget_menu_items_subsets[0].selected = True
    subset_select.value = 0
    assert subset_select.widget_menu_items_subsets[0].selected is True
    assert subset_select.widget_menu_items_subsets[1].selected is False

    # do multiple
    subset_select.widget_menu_item_select_multiple_checkbox.checked = True
    # now nothing should have changed in the selected subsets
    subset_select.value = [0, 1]
    assert subset_select.widget_menu_items_subsets[0].selected is True
    assert subset_select.widget_menu_items_subsets[1].selected is True
    subset_select.value = [0]
    assert subset_select.widget_menu_items_subsets[0].selected is True
    assert subset_select.widget_menu_items_subsets[1].selected is False

    # select multiple, then set multiple to false
    subset_select.value = [0, 1]
    assert subset_select.widget_menu_items_subsets[0].selected is True
    assert subset_select.widget_menu_items_subsets[1].selected is True
    subset_select.widget_menu_item_select_multiple_checkbox.checked = False
    assert subset_select.value == 0
    assert subset_select.widget_menu_items_subsets[0].selected is True
    assert subset_select.widget_menu_items_subsets[1].selected is False

    # switch multiple on again
    subset_select.widget_menu_item_select_multiple_checkbox.checked = True
    assert subset_select.value == [0]
    # and check again, now second selected
    subset_select.value = [1]
    subset_select.widget_menu_item_select_multiple_checkbox.checked = False
    assert subset_select.value == 1
    assert subset_select.widget_menu_items_subsets[0].selected is False
    assert subset_select.widget_menu_items_subsets[1].selected is True

    # if we deselect all, we should go to the 'new' state
    subset_select.value = []
    assert subset_select.widget_menu_items_subsets[0].selected is False
    assert subset_select.widget_menu_items_subsets[1].selected is False
    assert subset_select.value == 'new'
