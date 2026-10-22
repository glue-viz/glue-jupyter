import numpy as np
import pytest
from numpy.testing import assert_allclose

from glue.core import Data
from glue.core.coordinates import AffineCoordinates
from glue.core.link_helpers import LinkSame

from glue_jupyter.bqplot.common.line_layers import (BqplotVerticalLineLayerArtist,
                                                    BqplotHorizontalLineLayerArtist,
                                                    add_vertical_lines,
                                                    add_horizontal_lines)
from glue_jupyter.common.state_widgets.layer_line import LineLayerStateWidget
from glue_jupyter.tests.helpers import visual_widget_test


def make_lines(app, link_cid, positions=(1., 3., 2., 3.), label='lines'):
    lines = Data(position=list(positions), label=label)
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


def show_figure(viewer):
    figure = viewer.figure_widget
    figure.layout = {"width": "400px", "height": "250px"}
    return figure


# The setup for each viewer is shared between the tests that check the line
# positions and the visual tests. Horizontal lines are only available in the
# viewers that have a y attribute (scatter and image).


def setup_scatter_viewer(app, dataxyz):
    vlines = make_lines(app, dataxyz.id['x'], (1.5, 2.5, 2., 2.5), label='vlines')
    hlines = make_lines(app, dataxyz.id['y'], (2.5, 3.5, 3., 3.5), label='hlines')
    viewer = app.scatter2d(x='x', y='y', data=dataxyz, show=False)
    vartist = add_vertical_lines(viewer, vlines)
    vartist.state.color = 'red'
    hartist = add_horizontal_lines(viewer, hlines)
    hartist.state.color = 'blue'
    hartist.state.linestyle = 'dashed'
    return viewer, vartist, hartist


def test_scatter_viewer(app, dataxyz):

    viewer, vartist, hartist = setup_scatter_viewer(app, dataxyz)

    assert isinstance(vartist, BqplotVerticalLineLayerArtist)
    assert isinstance(hartist, BqplotHorizontalLineLayerArtist)
    assert vartist.enabled and hartist.enabled

    # Values are unique-d and sorted
    assert_positions(vartist, [1.5, 2, 2.5])
    assert_positions(hartist, [2.5, 3, 3.5], horizontal=True)

    # The scale along the lines is an independent [0:1] scale
    assert vartist.line_mark.scales['y'] is vartist.scale_along_lines
    assert hartist.line_mark.scales['x'] is hartist.scale_along_lines

    # The layer options widget resolves to the line layer widget
    widget_cls = viewer._layer_style_widget_cls[type(vartist)]
    assert widget_cls is LineLayerStateWidget
    widget_cls(vartist.state)


@visual_widget_test
def test_visual_scatter_viewer(tmp_path, page_session, solara_test, app, dataxyz):
    viewer, _, _ = setup_scatter_viewer(app, dataxyz)
    return show_figure(viewer)


def setup_profile_viewer(app):
    spectrum = Data(flux=np.sin(np.arange(10) / 2), label='spectrum')
    app.data_collection.append(spectrum)
    lines = make_lines(app, spectrum.pixel_component_ids[0])
    viewer = app.profile1d(data=spectrum, show=False)
    artist = add_vertical_lines(viewer, lines)
    artist.state.color = 'gray'
    artist.state.linestyle = 'dashed'
    # Subsets created after the fact follow the parent dataset
    app.data_collection.new_subset_group(label='high', subset_state=lines.id['position'] > 1.5)
    return viewer, lines, artist


def test_profile_viewer(app):

    viewer, lines, artist = setup_profile_viewer(app)

    assert artist.enabled
    assert_positions(artist, [1, 2, 3])

    subset_artists = [layer for layer in viewer.layers
                      if isinstance(layer, BqplotVerticalLineLayerArtist)
                      and layer.layer is not lines]
    assert len(subset_artists) == 1
    assert subset_artists[0].layer.data is lines
    assert_positions(subset_artists[0], [2, 3])

    # Horizontal lines are not available in the profile viewer
    with pytest.raises(ValueError, match='does not define a y axis'):
        add_horizontal_lines(viewer, lines)


@visual_widget_test
def test_visual_profile_viewer(tmp_path, page_session, solara_test, app):
    viewer, _, _ = setup_profile_viewer(app)
    return show_figure(viewer)


def test_profile_viewer_display_units(app):

    coords = AffineCoordinates(np.identity(2), units=['m'], labels=['position'])
    spectrum = Data(flux=np.random.random(10), coords=coords, label='spectrum')
    app.data_collection.append(spectrum)
    lines = make_lines(app, spectrum.world_component_ids[0])

    viewer = app.profile1d(data=spectrum)
    viewer.state.x_att = spectrum.world_component_ids[0]
    artist = add_vertical_lines(viewer, lines)

    assert viewer.state.x_display_unit == 'm'
    assert_positions(artist, [1, 2, 3])

    # The lines are converted to the display units of the x axis
    viewer.state.x_display_unit = 'cm'
    assert_positions(artist, [100, 200, 300])

    # Subsets created after the fact are converted too
    app.data_collection.new_subset_group(label='high', subset_state=lines.id['position'] > 1.5)
    subset_artist = [layer for layer in viewer.layers
                     if isinstance(layer, BqplotVerticalLineLayerArtist)
                     and layer.layer is not lines][0]
    assert_positions(subset_artist, [200, 300])

    viewer.state.x_display_unit = 'm'
    assert_positions(artist, [1, 2, 3])
    assert_positions(subset_artist, [2, 3])


def setup_histogram_viewer(app):
    data = Data(values=[1., 1., 2., 3., 5., 8.], label='data')
    app.data_collection.append(data)
    lines = make_lines(app, data.id['values'], (2.5, 6.5, 4.5, 6.5))
    viewer = app.histogram1d(x='values', data=data, show=False)
    artist = add_vertical_lines(viewer, lines)
    artist.state.color = 'black'
    artist.state.linestyle = 'dashdot'
    return viewer, artist


def test_histogram_viewer(app):

    viewer, artist = setup_histogram_viewer(app)

    assert artist.enabled
    assert_positions(artist, [2.5, 4.5, 6.5])

    # Updating the histogram visual attributes reorders the bars, which
    # should not fail on or drop the line mark
    viewer.state.x_log = True
    assert artist.line_mark in viewer.figure.marks


@visual_widget_test
def test_visual_histogram_viewer(tmp_path, page_session, solara_test, app):
    viewer, _ = setup_histogram_viewer(app)
    return show_figure(viewer)


def setup_image_viewer(app, data_image):
    vlines = make_lines(app, data_image.pixel_component_ids[1], (16., 48., 32., 48.),
                        label='vlines')
    hlines = make_lines(app, data_image.pixel_component_ids[0], (20., 40.), label='hlines')
    viewer = app.imshow(data=data_image, show=False)
    vartist = add_vertical_lines(viewer, vlines)
    vartist.state.color = 'cyan'
    hartist = add_horizontal_lines(viewer, hlines)
    hartist.state.color = 'magenta'
    hartist.state.linestyle = 'dotted'
    hartist.state.linewidth = 2
    return viewer, vartist, hartist


def test_image_viewer(app, data_image):

    _, vartist, hartist = setup_image_viewer(app, data_image)

    assert vartist.enabled and hartist.enabled
    assert_positions(vartist, [16, 32, 48])
    assert_positions(hartist, [20, 40], horizontal=True)


@visual_widget_test
def test_visual_image_viewer(tmp_path, page_session, solara_test, app, data_image):
    viewer, _, _ = setup_image_viewer(app, data_image)
    return show_figure(viewer)


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
