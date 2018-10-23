import pytest
import numpy as np

import glue_jupyter as gj
from glue.core.component_link import ComponentLink



def test_app(app, datax, dataxyz, dataxz):
    assert app._data[0] in [datax, dataxyz, dataxz]
    assert app.widget_selection_mode.index == 0
    assert len(app.widget_subset_groups.options) == 0
    assert len(app.widget_subset_groups.index) == 0
    app.subset_mode_and()
    assert app.widget_selection_mode.index == 2
    app.subset_mode_replace()
    assert app.widget_selection_mode.index == 0
    assert len(app.widget_subset_groups.index) == 0
    app.subset_lasso2d(dataxyz.id['x'], dataxyz.id['y'], [0.5, 2.5, 2.5, 0.5], [1, 1, 3.5, 3.5])

    assert len(app.widget_subset_groups.options) == len(app.data_collection.subset_groups)
    assert len(app.widget_subset_groups.index) == 1

    app.session.edit_subset_mode.edit_subset = [app.data_collection.subset_groups[0]]
    assert len(app.widget_subset_groups.index) == 1
    assert app.widget_subset_groups.index == (0,)

    app.session.edit_subset_mode.edit_subset = []
    assert len(app.widget_subset_groups.index) == 0
    assert app.widget_subset_groups.index == ()

    app.widget_subset_groups.index = (0,)
    assert app.session.edit_subset_mode.edit_subset == [app.data_collection.subset_groups[0]]

    app.session.edit_subset_mode.edit_subset = []
    assert len(app.widget_subset_groups.index) == 0
    assert dataxyz.subsets[0]['x'].tolist() == [1, 2]
    assert dataxyz.subsets[0]['y'].tolist() == [2, 3]
    assert dataxyz.subsets[0]['z'].tolist() == [5, 6]


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





def test_double_load_data(tmpdir):

    # Regression test for a bug that caused a crash when adding two datasets
    # with the same shape.

    filename = tmpdir.join('data1.csv').strpath

    with open(filename, 'w') as f:
        f.write('a,b\n1,2\n3,4\n5.6\n')

    app = gj.jglue()
    app.load_data(filename)
    app.load_data(filename)
