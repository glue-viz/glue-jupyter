from glue.core.edit_subset_mode import OrMode, ReplaceMode


def test_subset_mode(app, datax, dataxyz, dataxz):
    subset_mode = app.widget_subset_mode

    # glue -> ui sync
    assert subset_mode.widget_selection_mode.value == 0
    app.subset_mode_and()
    assert subset_mode.widget_selection_mode.value == 2
    app.subset_mode_replace()
    assert subset_mode.widget_selection_mode.value == 0

    # ui -> glue sync
    subset_mode.widget_selection_mode.value = 1
    assert app.session.edit_subset_mode.mode == OrMode
    subset_mode.widget_selection_mode.value = 0
    assert app.session.edit_subset_mode.mode == ReplaceMode
