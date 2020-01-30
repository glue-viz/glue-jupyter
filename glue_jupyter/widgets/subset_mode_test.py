from glue.core.edit_subset_mode import OrMode, ReplaceMode


def test_subset_mode(app, datax, dataxyz, dataxz):
    subset_mode = app.widget_subset_mode

    # glue -> ui sync
    assert subset_mode.main.children[0] is subset_mode.modes[0][1]
    app.set_subset_mode('and')
    assert subset_mode.main.children[0] is subset_mode.modes[2][1]
    app.set_subset_mode('replace')
    assert subset_mode.main.children[0] is subset_mode.modes[0][1]

    # ui -> glue sync
    subset_mode.children[0].children[1].fire_event('click', {})
    assert app.session.edit_subset_mode.mode == OrMode
    subset_mode.children[0].children[0].fire_event('click', {})
    assert app.session.edit_subset_mode.mode == ReplaceMode
