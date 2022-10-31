import glue_jupyter as gj
from glue.core import Data


def test_non_hex_colors(app, dataxyz):

    # Make sure non-hex colors such as '0.4' and 'red', which are valid
    # matplotlib colors, work as expected.

    viewer = app.histogram1d(data=dataxyz)
    dataxyz.style.color = '0.3'
    dataxyz.style.color = 'indigo'

    app.subset('test', dataxyz.id['x'] > 1)
    viewer.layer_options.selected = 1
    dataxyz.subsets[0].style.color = '0.5'
    dataxyz.subsets[0].style.color = 'purple'


def test_remove(app, dataxz, dataxyz):
    s = app.histogram1d(data=dataxyz)
    s.add_data(dataxz)
    app.data_collection.new_subset_group(subset_state=dataxz.id['x'] > 1, label='test')
    assert len(s.figure_widget.marks) == 4
    s.remove_data(dataxyz)
    assert len(s.figure_widget.marks) == 2
    s.remove_data(dataxz)
    assert len(s.figure_widget.marks) == 0


def test_normalize():
    data = Data(x=[1, 2, 3, 4], label="x data")
    app = gj.jglue(data=data)
    s = app.histogram1d(data=data)
    s.state.hist_x_min = 0
    s.state.hist_x_max = 5
    s.state.hist_n_bin = 5
    assert len(s.figure_widget.marks) == 1
    assert s.figure_widget.marks[0].x.tolist() == [0.5, 1.5, 2.5, 3.5, 4.5]
    assert s.figure_widget.marks[0].y.tolist() == [1.0, 1.0, 1.0, 1.0, 0.0]
    s.state.normalize = True
    assert s.figure_widget.marks[0].y.tolist() == [1/4., 1/4., 1/4., 1/4., 0.0]
