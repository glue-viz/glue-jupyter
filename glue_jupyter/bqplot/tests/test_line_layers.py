import numpy as np
import pytest
from numpy.testing import assert_allclose

from glue.core import Data
from glue.core.link_helpers import LinkSame

from glue_jupyter.bqplot.common.line_layers import (BqplotVerticalLineLayerArtist,
                                                    BqplotHorizontalLineLayerArtist,
                                                    add_vertical_lines,
                                                    add_horizontal_lines)
from glue_jupyter.common.state_widgets.layer_line import LineLayerStateWidget


def make_lines(app, link_cid):
    lines = Data(position=[1., 3., 2., 3.], label='lines')
    app.data_collection.append(lines)
    app.data_collection.add_link(LinkSame(lines.id['position'], link_cid))
    return lines


def assert_positions(artist, expected, horizontal=False):
    across = artist.line_mark.y if horizontal else artist.line_mark.x
    along = artist.line_mark.x if horizontal else artist.line_mark.y
    # Each line is rendered as three vertices (start, end, NaN separator)
    assert_allclose(across[::3], expected)
    assert_allclose(across[1::3], expected)
    assert_allclose(along[:2], [0, 1])


def test_scatter_viewer(app, dataxyz):

    lines = make_lines(app, dataxyz.id['x'])
    app.data_collection.add_link(LinkSame(lines.id['position'], dataxyz.id['y']))

    viewer = app.scatter2d(x='x', y='y', data=dataxyz)
    vartist = add_vertical_lines(viewer, lines)
    hartist = add_horizontal_lines(viewer, lines)

    assert isinstance(vartist, BqplotVerticalLineLayerArtist)
    assert isinstance(hartist, BqplotHorizontalLineLayerArtist)
    assert vartist.enabled and hartist.enabled

    # Values are unique-d and sorted
    assert_positions(vartist, [1, 2, 3])
    assert_positions(hartist, [1, 2, 3], horizontal=True)

    # The scale along the lines is an independent [0:1] scale
    assert vartist.line_mark.scales['y'] is vartist.scale_along_lines
    assert hartist.line_mark.scales['x'] is hartist.scale_along_lines

    # The layer options widget resolves to the line layer widget
    widget_cls = viewer._layer_style_widget_cls[type(vartist)]
    assert widget_cls is LineLayerStateWidget
    widget_cls(vartist.state)


def test_profile_viewer(app):

    spectrum = Data(flux=np.random.random(10), label='spectrum')
    app.data_collection.append(spectrum)
    lines = make_lines(app, spectrum.pixel_component_ids[0])

    viewer = app.profile1d(data=spectrum)
    artist = add_vertical_lines(viewer, lines)

    assert artist.enabled
    assert_positions(artist, [1, 2, 3])

    # Subsets created after the fact follow the parent dataset
    app.data_collection.new_subset_group(label='high', subset_state=lines.id['position'] > 1.5)

    subset_artists = [layer for layer in viewer.layers
                      if isinstance(layer, BqplotVerticalLineLayerArtist)
                      and layer.layer is not lines]
    assert len(subset_artists) == 1
    assert subset_artists[0].layer.data is lines
    assert_positions(subset_artists[0], [2, 3])

    # Horizontal lines are not available in the profile viewer
    with pytest.raises(ValueError, match='does not define a y axis'):
        add_horizontal_lines(viewer, lines)


def test_histogram_viewer(app):

    data = Data(values=[1., 1., 2., 3., 5., 8.], label='data')
    app.data_collection.append(data)
    lines = make_lines(app, data.id['values'])

    viewer = app.histogram1d(x='values', data=data)
    artist = add_vertical_lines(viewer, lines)

    assert artist.enabled
    assert_positions(artist, [1, 2, 3])


def test_image_viewer(app, data_image):

    lines = make_lines(app, data_image.pixel_component_ids[1])

    viewer = app.imshow(data=data_image)
    artist = add_vertical_lines(viewer, lines)

    assert artist.enabled
    assert_positions(artist, [1, 2, 3])


def test_styling(app, dataxyz):

    lines = make_lines(app, dataxyz.id['x'])
    lines.style.color = '#ff0000'

    viewer = app.scatter2d(x='x', y='y', data=dataxyz)
    artist = add_vertical_lines(viewer, lines)

    assert artist.line_mark.colors == ['#ff0000']

    artist.state.linewidth = 3
    assert artist.line_mark.stroke_width == 3

    artist.state.linestyle = 'dashdot'
    assert artist.line_mark.line_style == 'dash_dotted'

    artist.state.visible = False
    assert not artist.line_mark.visible

    # Removing the layer removes the mark
    viewer.remove_data(lines)
    assert not any(isinstance(layer, BqplotVerticalLineLayerArtist)
                   for layer in viewer.layers)


def test_many_lines(app, dataxyz):

    # All the lines are rendered as a single NaN-separated mark so this
    # should remain fast even for many thousands of lines

    lines = Data(position=np.random.random(20000) * 3, label='lines')
    app.data_collection.append(lines)
    app.data_collection.add_link(LinkSame(lines.id['position'], dataxyz.id['x']))

    viewer = app.scatter2d(x='x', y='y', data=dataxyz)
    n_marks = len(viewer.figure.marks)
    artist = add_vertical_lines(viewer, lines)

    assert len(viewer.figure.marks) == n_marks + 1
    assert len(artist.line_mark.x) == 60000
    assert artist.line_mark.x.dtype == np.float32
