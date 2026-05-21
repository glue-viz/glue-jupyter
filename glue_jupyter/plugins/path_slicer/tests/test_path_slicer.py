"""
Tests for the glue-jupyter path slicer plugin. The data-side helper is
exercised against both backends; the bqplot and matplotlib mode classes
are imported and instantiated lightly to make sure their constructors
don't blow up. Full interactive-event coverage is out of scope.
"""
import numpy as np

from glue.core import Data
from glue.core.coordinates import IdentityCoordinates
from glue.plugins.tools.path_slicer.path_sliced_data import PathSlicedData
from glue.plugins.tools.path_slicer.path_sliced_data_links import (
    link_path_sliced_to_parent, link_path_sliced_pair_paths)

from glue_jupyter import jglue
from glue_jupyter.bqplot.image import BqplotImageView
from glue_jupyter.matplotlib.image import ImageJupyterViewer

from glue.plugins.tools.path_slicer.common import (
    build_or_update_path_slices, path_link_exists, drive_parent_slice)
from ..bqplot import BqplotPathSlicerMode
from ..matplotlib import MatplotlibJupyterPathSlicerMode


def _make_app_with_cube():
    cube = Data(label='cube',
                x=np.arange(120.).reshape((6, 5, 4)),
                coords=IdentityCoordinates(n_dim=3))
    app = jglue()
    app.data_collection.append(cube)
    return app, cube


def test_tools_registered():
    # Loaded via the ``glue.plugins`` entry point in pyproject.toml; the
    # setup function wires the tool IDs onto the image viewers.
    from glue.main import load_plugins  # noqa: PLC0415
    load_plugins()
    assert 'jupyter:slice' in ImageJupyterViewer.tools
    assert 'jupyter:path_crosshair' in ImageJupyterViewer.tools
    assert 'bqplot:slice' in BqplotImageView.tools
    assert 'bqplot:path_crosshair' in BqplotImageView.tools


def test_build_or_update_path_slices_creates_path_sliced_data_via_bqplot():
    app, cube = _make_app_with_cube()
    viewer = app.new_data_viewer(BqplotImageView, data=cube)
    updated = build_or_update_path_slices(viewer, vx=[1, 2, 3], vy=[0, 1, 2])
    assert len(updated) == 1
    path_slice, _ = updated[0]
    assert isinstance(path_slice, PathSlicedData)
    assert path_slice.original_data is cube
    assert path_slice in app.data_collection


def test_build_or_update_path_slices_reuses_existing():
    app, cube = _make_app_with_cube()
    viewer = app.new_data_viewer(BqplotImageView, data=cube)
    first = build_or_update_path_slices(viewer, [1, 2, 3], [0, 1, 2])[0][0]
    first_x = first.x.copy()
    updated = build_or_update_path_slices(viewer, [0, 5, 2], [4, 0, 3])
    assert len(updated) == 1
    assert updated[0][0] is first
    # set_xy must have replaced x.
    assert not np.array_equal(first_x, updated[0][0].x)


def test_path_link_exists_after_pair():
    # With two PathSlicedDatas and the pairwise link in place,
    # path_link_exists must report True. Construct them manually --
    # build_or_update_path_slices's "reuse existing" branch would otherwise
    # collapse them onto a single slice.
    app, cube = _make_app_with_cube()
    slice1 = PathSlicedData(cube, cube.pixel_component_ids[1], [0., 1., 2.],
                         cube.pixel_component_ids[2], [0., 1., 2.])
    slice2 = PathSlicedData(cube, cube.pixel_component_ids[1], [0., 1., 2., 3.],
                         cube.pixel_component_ids[2], [0., 1., 2., 3.])
    app.data_collection.append(slice1)
    app.data_collection.append(slice2)
    link_path_sliced_to_parent(app.data_collection, slice1)
    link_path_sliced_to_parent(app.data_collection, slice2)
    assert not path_link_exists(app.data_collection, slice1, slice2)
    link_path_sliced_pair_paths(app.data_collection, slice1, slice2)
    assert path_link_exists(app.data_collection, slice1, slice2)


def test_bqplot_mode_construction_and_event_routing():
    app, cube = _make_app_with_cube()
    viewer = app.new_data_viewer(BqplotImageView, data=cube)
    mode = BqplotPathSlicerMode(viewer)
    mode.activate()
    mode._on_event({'event': 'click', 'domain': {'x': 1.0, 'y': 0.5}})
    mode._on_event({'event': 'click', 'domain': {'x': 2.5, 'y': 1.5}})
    mode._on_event({'event': 'keydown', 'key': 'Enter'})
    # After Enter, a slice viewer was opened and a PathSlicedData appended
    # to the data collection.
    assert mode._slice_viewer is not None
    slices = [d for d in app.data_collection if isinstance(d, PathSlicedData)]
    assert len(slices) == 1
    mode.deactivate()


def test_bqplot_mode_escape_clears_in_progress_path():
    app, cube = _make_app_with_cube()
    viewer = app.new_data_viewer(BqplotImageView, data=cube)
    mode = BqplotPathSlicerMode(viewer)
    mode.activate()
    mode._on_event({'event': 'click', 'domain': {'x': 1.0, 'y': 0.5}})
    mode._on_event({'event': 'click', 'domain': {'x': 2.5, 'y': 1.5}})
    assert mode._vx == [1.0, 2.5]
    mode._on_event({'event': 'keydown', 'key': 'Escape'})
    assert mode._vx == []
    assert mode._vy == []
    slices = [d for d in app.data_collection if isinstance(d, PathSlicedData)]
    assert slices == []
    mode.deactivate()


def test_drive_parent_slice_updates_state_slices():
    # The slice crosshair tool calls drive_parent_slice when the mouse
    # moves in the slice viewer. Verify it writes to the parent's
    # state.slices regardless of backend.
    for ViewerCls in (BqplotImageView, ImageJupyterViewer):
        app, cube = _make_app_with_cube()
        viewer = app.new_data_viewer(ViewerCls, data=cube)
        path_slice = PathSlicedData(cube, cube.pixel_component_ids[1], [0., 1., 2.],
                            cube.pixel_component_ids[2], [0., 1., 2.])
        path_slice.parent_viewer = viewer
        before = tuple(viewer.state.slices)
        drive_parent_slice(path_slice, 3.0)
        after = tuple(viewer.state.slices)
        assert after != before
        # The axis that changed is the one that's not x_att.axis or y_att.axis.
        slice_axis = next(i for i in range(cube.ndim)
                          if i not in (viewer.state.x_att.axis,
                                       viewer.state.y_att.axis))
        assert after[slice_axis] == 3


def test_crosshair_tool_hidden_on_cube_viewer():
    # The crosshair tool is registered on both ImageJupyterViewer and
    # BqplotImageView, but only meaningful on a slice viewer. The toolbar
    # must hide it (drop the entry from tools_data) when the tool reports
    # enabled=False at the time it's added to the toolbar.
    app, cube = _make_app_with_cube()
    viewer = app.new_data_viewer(ImageJupyterViewer, data=cube)
    assert 'jupyter:path_crosshair' not in viewer.toolbar.tools_data


def test_matplotlib_mode_constructible():
    # We don't simulate the matplotlib event loop here; just check the
    # mode can be constructed against an ImageJupyterViewer (matplotlib
    # backend in the browser).
    app, cube = _make_app_with_cube()
    viewer = app.new_data_viewer(ImageJupyterViewer, data=cube)
    mode = MatplotlibJupyterPathSlicerMode(viewer)
    assert mode._slice_viewer is None
    assert mode.enabled is True  # cube is 3-d


# ---------------------------------------------------------------------------
# Multi-trace + toolbar-menu behaviour (Jupyter side)
# ---------------------------------------------------------------------------


def test_toolbar_menu_labels_track_traces():
    # The vuetify toolbar reads ``tool.menu_entries()`` and exposes the
    # labels (and a checkmark for the active target) to the Vue
    # template via ``tools_data``. Each new trace adds a new entry,
    # and the active checkmark moves with ``set_target``.
    app, cube = _make_app_with_cube()
    viewer = app.new_data_viewer(ImageJupyterViewer, data=cube)
    slice_tool = viewer.toolbar.tools['jupyter:slice']

    entry = viewer.toolbar.tools_data['jupyter:slice']
    assert entry['menu_labels'] == ['Create new path']
    assert entry['menu_active_index'] == 0

    slice_tool._open_or_update([1., 2., 3.], [0., 1., 2.])
    entry = viewer.toolbar.tools_data['jupyter:slice']
    assert entry['menu_labels'] == ['Create new path', 'Update path 1']
    # The newly-created trace is the active target -> index 1.
    assert entry['menu_active_index'] == 1

    slice_tool.set_target(None)
    entry = viewer.toolbar.tools_data['jupyter:slice']
    assert entry['menu_active_index'] == 0

    slice_tool._open_or_update([0., 5., 2.], [4., 0., 3.])
    entry = viewer.toolbar.tools_data['jupyter:slice']
    assert entry['menu_labels'] == [
        'Create new path', 'Update path 1', 'Update path 2']
    assert entry['menu_active_index'] == 2


def test_vue_select_menu_item_routes_to_set_target():
    # The Vue template calls ``select_menu_item({tool_id, index})``
    # on the toolbar widget; the resulting ``vue_select_menu_item``
    # method looks the target up in the tool's menu and calls
    # ``set_target``.
    app, cube = _make_app_with_cube()
    viewer = app.new_data_viewer(ImageJupyterViewer, data=cube)
    slice_tool = viewer.toolbar.tools['jupyter:slice']

    slice_tool._open_or_update([1., 2., 3.], [0., 1., 2.])
    slice_tool.set_target(None)
    slice_tool._open_or_update([0., 5., 2.], [4., 0., 3.])

    # Simulate the user clicking "Update path 1" -- index 1 in the
    # menu: ['Create new path', 'Update path 1', 'Update path 2'].
    viewer.toolbar.vue_select_menu_item({'tool_id': 'jupyter:slice',
                                         'index': 1})
    assert slice_tool._target_trace is slice_tool._traces[0]


def test_bqplot_mode_multi_trace_create_then_update():
    app, cube = _make_app_with_cube()
    viewer = app.new_data_viewer(BqplotImageView, data=cube)
    mode = BqplotPathSlicerMode(viewer)
    mode.activate()

    mode._on_event({'event': 'click', 'domain': {'x': 1.0, 'y': 0.5}})
    mode._on_event({'event': 'click', 'domain': {'x': 2.5, 'y': 1.5}})
    mode._on_event({'event': 'keydown', 'key': 'Enter'})
    assert len(mode._traces) == 1
    assert len(mode._slice_viewers) == 1
    first_slice_viewer = mode._slice_viewers[0]
    first_x = mode._traces[0][0].x.copy()

    # Pick "Create new path" via the toolbar dropdown, draw again -> trace 2.
    mode.set_target(None)
    mode._on_event({'event': 'click', 'domain': {'x': 0.5, 'y': 1.5}})
    mode._on_event({'event': 'click', 'domain': {'x': 3.0, 'y': 2.5}})
    mode._on_event({'event': 'keydown', 'key': 'Enter'})
    assert len(mode._traces) == 2
    assert len(mode._slice_viewers) == 2
    assert mode._slice_viewers[0] is first_slice_viewer

    # Trace 1 must not have been disturbed.
    assert np.array_equal(mode._traces[0][0].x, first_x)
    mode.deactivate()


def test_bqplot_mode_overlays_per_trace():
    app, cube = _make_app_with_cube()
    viewer = app.new_data_viewer(BqplotImageView, data=cube)
    mode = BqplotPathSlicerMode(viewer)
    mode.activate()

    # Draw two traces.
    for vx, vy in [([1.0, 2.5], [0.5, 1.5]),
                   ([0.5, 3.0], [1.5, 2.5])]:
        mode.set_target(None)
        for x, y in zip(vx, vy):
            mode._on_event({'event': 'click', 'domain': {'x': x, 'y': y}})
        mode._on_event({'event': 'keydown', 'key': 'Enter'})

    assert len(mode._overlays) == 2
    active = mode._overlays[id(mode._traces[1])]
    other = mode._overlays[id(mode._traces[0])]
    assert active.opacities[0] > other.opacities[0]
    mode.deactivate()
