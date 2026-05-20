"""
Helpers shared between the bqplot and matplotlib PV slicer tools.
"""
import numpy as np

from glue.core import Data
from glue.plugins.tools.pv_slicer.path_sliced_data import PathSlicedData
from glue.plugins.tools.pv_slicer.path_sliced_data_links import (
    link_path_sliced_to_parent, link_path_sliced_pair_paths)


__all__ = ['build_or_update_pvs', 'path_link_exists']


def path_link_exists(dc, pv_a, pv_b):
    """True if the link graph already has a link involving the path
    pixel CIDs of both PVs."""
    cid_a = pv_a.pixel_component_ids[-1]
    cid_b = pv_b.pixel_component_ids[-1]
    for link in dc.external_links:
        ends = list(getattr(link, '_from', []))
        to = getattr(link, '_to', None)
        if to is not None:
            ends.append(to)
        if cid_a in ends and cid_b in ends:
            return True
    return False


def build_or_update_pvs(source_viewer, vx, vy):
    """
    For each Data layer in ``source_viewer``, create (or update in
    place) the corresponding PathSlicedData, register the needed
    ComponentLinks, and return the list of (PV, source layer state)
    pairs in iteration order.

    The caller is responsible for opening / reusing a PV viewer and
    populating it with the returned PVs; this helper does only the
    data-model side of the work.
    """
    dc = source_viewer.session.data_collection
    x_att = source_viewer.state.x_att
    y_att = source_viewer.state.y_att
    vx = np.asarray(vx)
    vy = np.asarray(vy)

    updated = []
    for layer_state in source_viewer.state.layers:
        data = layer_state.layer
        if not isinstance(data, Data):
            # Subsets ride along with their parent Data.
            continue

        existing = _find_existing_pv(dc, data)
        if existing is None:
            pv = PathSlicedData(data, x_att, vx, y_att, vy,
                                label=data.label + ' [slice]')
            pv.parent_viewer = source_viewer
            dc.append(pv)
            link_path_sliced_to_parent(dc, pv)
        else:
            pv = existing
            pv.cid_x = x_att
            pv.cid_y = y_att
            pv.sliced_dims = (x_att.axis, y_att.axis)
            pv.set_xy(vx, vy)
        updated.append((pv, layer_state))

    for i, (pv_a, _) in enumerate(updated):
        for pv_b, _ in updated[i + 1:]:
            if not path_link_exists(dc, pv_a, pv_b):
                link_path_sliced_pair_paths(dc, pv_a, pv_b)

    return updated


def _find_existing_pv(dc, parent_data):
    for d in dc:
        if isinstance(d, PathSlicedData) and d.original_data is parent_data:
            return d
    return None
