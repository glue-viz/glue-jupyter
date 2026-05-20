"""
Tests for the glue-jupyter PV slicer plugin. The data-side helper is
exercised against both backends; the bqplot and matplotlib mode classes
are imported and instantiated lightly to make sure their constructors
don't blow up. Full interactive-event coverage is out of scope.
"""
import numpy as np

from glue.core import Data
from glue.core.coordinates import IdentityCoordinates
from glue.plugins.tools.pv_slicer.path_sliced_data import PathSlicedData
from glue.plugins.tools.pv_slicer.path_sliced_data_links import (
    link_path_sliced_to_parent, link_path_sliced_pair_paths)

from glue_jupyter import jglue
from glue_jupyter.bqplot.image import BqplotImageView
from glue_jupyter.matplotlib.image import ImageJupyterViewer

from ..common import build_or_update_pvs, path_link_exists
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
    # The plugin's __init__ runs on import; the tool IDs must end up on
    # the corresponding viewers.
    assert 'jupyter:slice' in ImageJupyterViewer.tools
    assert 'jupyter:pv_crosshair' in ImageJupyterViewer.tools
    assert 'bqplot:slice' in BqplotImageView.tools
    assert 'bqplot:pv_crosshair' in BqplotImageView.tools


def test_build_or_update_pvs_creates_path_sliced_data_via_bqplot():
    app, cube = _make_app_with_cube()
    viewer = app.new_data_viewer(BqplotImageView, data=cube)
    updated = build_or_update_pvs(viewer, vx=[1, 2, 3], vy=[0, 1, 2])
    assert len(updated) == 1
    pv, _ = updated[0]
    assert isinstance(pv, PathSlicedData)
    assert pv.original_data is cube
    assert pv in app.data_collection


def test_build_or_update_pvs_reuses_existing():
    app, cube = _make_app_with_cube()
    viewer = app.new_data_viewer(BqplotImageView, data=cube)
    first = build_or_update_pvs(viewer, [1, 2, 3], [0, 1, 2])[0][0]
    first_x = first.x.copy()
    updated = build_or_update_pvs(viewer, [0, 5, 2], [4, 0, 3])
    assert len(updated) == 1
    assert updated[0][0] is first
    # set_xy must have replaced x.
    assert not np.array_equal(first_x, updated[0][0].x)


def test_path_link_exists_after_pair():
    # With two PathSlicedDatas and the pairwise link in place,
    # path_link_exists must report True. Construct them manually --
    # build_or_update_pvs's "reuse existing" branch would otherwise
    # collapse them onto a single PV.
    app, cube = _make_app_with_cube()
    pv1 = PathSlicedData(cube, cube.pixel_component_ids[1], [0., 1., 2.],
                         cube.pixel_component_ids[2], [0., 1., 2.])
    pv2 = PathSlicedData(cube, cube.pixel_component_ids[1], [0., 1., 2., 3.],
                         cube.pixel_component_ids[2], [0., 1., 2., 3.])
    app.data_collection.append(pv1)
    app.data_collection.append(pv2)
    link_path_sliced_to_parent(app.data_collection, pv1)
    link_path_sliced_to_parent(app.data_collection, pv2)
    assert not path_link_exists(app.data_collection, pv1, pv2)
    link_path_sliced_pair_paths(app.data_collection, pv1, pv2)
    assert path_link_exists(app.data_collection, pv1, pv2)


def test_bqplot_mode_construction_and_event_routing():
    app, cube = _make_app_with_cube()
    viewer = app.new_data_viewer(BqplotImageView, data=cube)
    mode = BqplotPathSlicerMode(viewer)
    mode.activate()
    mode._on_event({'event': 'click', 'domain': {'x': 1.0, 'y': 0.5}})
    mode._on_event({'event': 'click', 'domain': {'x': 2.5, 'y': 1.5}})
    mode._on_event({'event': 'keydown', 'key': 'Enter'})
    # After Enter, a PV viewer was opened and a PathSlicedData appended
    # to the data collection.
    assert mode._pv_viewer is not None
    pvs = [d for d in app.data_collection if isinstance(d, PathSlicedData)]
    assert len(pvs) == 1
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
    pvs = [d for d in app.data_collection if isinstance(d, PathSlicedData)]
    assert pvs == []
    mode.deactivate()


def test_matplotlib_mode_constructible():
    # We don't simulate the matplotlib event loop here; just check the
    # mode can be constructed against an ImageJupyterViewer (matplotlib
    # backend in the browser).
    app, cube = _make_app_with_cube()
    viewer = app.new_data_viewer(ImageJupyterViewer, data=cube)
    mode = MatplotlibJupyterPathSlicerMode(viewer)
    assert mode._pv_viewer is None
    assert mode.enabled is True  # cube is 3-d
