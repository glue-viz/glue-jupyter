import pytest
import numpy as np

import glue_jupyter as gj
from glue.core.component_link import ComponentLink



def test_app(app, datax, dataxyz, dataxz):
    assert app._data[0] in [datax, dataxyz, dataxz]
    assert app.widget_selection_mode.index == 0

    # if there are no subsets, you cannot select multiple
    assert app.widget_subset_group_menu_item_select_multiple.enabled == False
    assert app.widget_subset_group_menu_item_no_active
    assert app.widget_subset_group_button.description == app.widget_subset_group_menu_item_no_active.description


    assert len(app.widget_subset_groups.options) == 0
    assert len(app.widget_subset_groups.index) == 0
    app.subset_mode_and()
    assert app.widget_selection_mode.index == 2
    app.subset_mode_replace()
    assert app.widget_selection_mode.index == 0
    assert len(app.widget_subset_groups.index) == 0


    # now we make a section
    app.subset_lasso2d(dataxyz.id['x'], dataxyz.id['y'], [0.5, 2.5, 2.5, 0.5], [1, 1, 3.5, 3.5])

    assert len(app.widget_subset_group_menu_items_subsets) == 1
    assert app.widget_subset_group_button.description == app.widget_subset_group_menu_items_subsets[0].description
    assert app.widget_subset_group_menu_item_no_active.value == False

    assert len(app.widget_subset_groups.options) == len(app.data_collection.subset_groups)
    assert len(app.widget_subset_groups.index) == 1

    app.session.edit_subset_mode.edit_subset = [app.data_collection.subset_groups[0]]
    assert len(app.widget_subset_groups.index) == 1
    assert app.widget_subset_groups.index == (0,)
    assert app.widget_subset_group_menu_item_no_active.value == False
    assert app.widget_subset_group_menu_items_subsets[0].value == True


    app.session.edit_subset_mode.edit_subset = []
    assert app.widget_subset_group_menu_item_no_active.value == True
    assert app.widget_subset_group_menu_items_subsets[0].value == False
    assert len(app.widget_subset_groups.index) == 0
    assert app.widget_subset_groups.index == ()

    app.widget_subset_groups.index = (0,)
    assert app.session.edit_subset_mode.edit_subset == [app.data_collection.subset_groups[0]]
    assert app.widget_subset_group_menu_item_no_active.value == False
    assert app.widget_subset_group_menu_items_subsets[0].value == True

    app.session.edit_subset_mode.edit_subset = []
    assert len(app.widget_subset_groups.index) == 0
    assert dataxyz.subsets[0]['x'].tolist() == [1, 2]
    assert dataxyz.subsets[0]['y'].tolist() == [2, 3]
    assert dataxyz.subsets[0]['z'].tolist() == [5, 6]

    # now do a second selection
    app.session.edit_subset_mode.edit_subset = [app.data_collection.subset_groups[0]]
    assert app.widget_subset_group_menu_items_subsets[0].value == True
    assert app.widget_subset_group_menu_item_no_active.value == False

    app.widget_subset_group_menu_item_no_active.value = True
    assert app.session.edit_subset_mode.edit_subset == [], 'should have triggered nothing to be selected'
    assert app.widget_subset_group_menu_items_subsets[0].value == False

    app.subset_lasso2d(dataxyz.id['x'], dataxyz.id['y'], [0.5, 2.5, 2.5, 0.5], [1, 1, 3.5, 3.5])
    assert app.widget_subset_group_menu_item_no_active.value == False
    assert app.widget_subset_group_menu_items_subsets[0].value == False
    assert app.widget_subset_group_menu_items_subsets[1].value == True

    # we do not have multiple subsets enabled
    app.widget_subset_group_menu_items_subsets[0].value = True
    assert app.widget_subset_group_menu_items_subsets[0].value == True
    assert app.widget_subset_group_menu_items_subsets[1].value == False

    # do multiple
    app.widget_subset_group_menu_item_select_multiple.value = True
    # now nothing should have changed in the selected subsets
    assert app.widget_subset_group_menu_items_subsets[0].value == True
    assert app.widget_subset_group_menu_items_subsets[1].value == False
    # now we do have it enabled, so we can select the second one
    app.widget_subset_group_menu_items_subsets[1].value = True
    assert app.widget_subset_group_menu_items_subsets[0].value == True
    assert app.widget_subset_group_menu_items_subsets[1].value == True

    # TODO: not implemented yet.. not sure if we want this
    if 0:
        # we disabled it again, so now the first one should be selected
        app.widget_subset_group_menu_item_select_multiple.value = False
        assert app.widget_subset_group_menu_items_subsets[0].value == True
        assert app.widget_subset_group_menu_items_subsets[1].value == False

        # we should not be able to deselect the last one
        app.widget_subset_group_menu_items_subsets[0].value = False
        assert app.widget_subset_group_menu_items_subsets[0].value == True
        assert app.widget_subset_group_menu_items_subsets[1].value == False


def test_default_components(app, datax, dataxz, dataxyz):
    s = app.scatter2d(data=datax)
    assert s.state.x_att is datax.main_components[0]

    s = app.scatter2d(data=dataxz)
    assert s.state.x_att is dataxz.main_components[0]
    assert s.state.y_att is dataxz.main_components[1]

    s = app.scatter3d(data=datax)
    assert s.state.x_att is datax.main_components[0]

    s = app.scatter3d(data=dataxz)
    assert s.state.x_att is dataxz.main_components[0]
    assert s.state.y_att is dataxz.main_components[1]

    s = app.scatter3d(data=dataxyz)
    assert s.state.x_att is dataxyz.main_components[0]
    assert s.state.y_att is dataxyz.main_components[1]
    assert s.state.z_att is dataxyz.main_components[2]


def test_viewer_state(app, dataxyz):
    s = app.scatter2d('x', 'y', data=dataxyz, viewer_state=dict(x_att=dataxyz.id['y'], y_att=dataxyz.id['z'], x_min=-1, x_max=1))
    # direct argument have preference over the viewer_state
    assert s.state.x_att is dataxyz.id['x']
    assert s.state.y_att is dataxyz.id['y']
    assert s.state.x_min == -1
    assert s.state.x_max == 1

    # was testing with x_min, but it gets reset to hist_x_min
    s = app.histogram1d('y', data=dataxyz, viewer_state=dict(x_att=dataxyz.id['z'], hist_x_min=-1, hist_x_max=1))
    assert s.state.x_att is dataxyz.id['y']
    assert s.state.hist_x_min == -1
    assert s.state.hist_x_max == 1

    # x_min is used for the API, this sets viewer.state.hist_x_min/max which sets again viewer.state.x_min
    s = app.histogram1d('y', data=dataxyz, x_min=-2, x_max=2)
    assert s.state.x_att is dataxyz.id['y']
    assert s.state.hist_x_min == -2
    assert s.state.hist_x_max == 2
    assert s.state.x_min == -2
    assert s.state.x_max == 2

def test_layer_state(app, dataxyz):
    s = app.scatter2d(data=dataxyz, layer_state=dict(size=10))
    assert s.layers[0].state.size == 10
    # direct argument have preference over the layer_state
    s = app.scatter2d(data=dataxyz, size=11, layer_state=dict(size=10))
    assert s.layers[0].state.size == 11

    s = app.histogram1d('x', data=dataxyz, layer_state=dict(color='green'))
    assert s.layers[0].state.color == 'green'


def test_add_data_with_state(app, dataxz, dataxyz):
    s = app.scatter2d('x', 'z', data=dataxz, color='green')
    s.add_data(dataxyz, color='red', alpha=0.2, size=3.3)
    assert s.layers[0].state.color == 'green'
    assert s.layers[1].state.color == 'red'
    assert s.layers[1].state.alpha == 0.2
    assert s.layers[1].state.size == 3.3

def test_double_load_data(tmpdir):

    # Regression test for a bug that caused a crash when adding two datasets
    # with the same shape.

    filename = tmpdir.join('data1.csv').strpath

    with open(filename, 'w') as f:
        f.write('a,b\n1,2\n3,4\n5.6\n')

    app = gj.jglue()
    app.load_data(filename)
    app.load_data(filename)
