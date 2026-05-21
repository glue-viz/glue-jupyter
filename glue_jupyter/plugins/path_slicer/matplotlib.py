"""
glue-jupyter wrapper around glue-core's matplotlib path slicer modes.
The multi-trace data model and matplotlib path overlays live in
:mod:`glue.plugins.tools.path_slicer.matplotlib_mode`. The dropdown
menu UI (Create new path / Update path N) is rendered by the vuetify
toolbar: any tool that exposes ``menu_entries()`` gets a chevron
button beside its main icon -- see
:mod:`glue_jupyter.common.toolbar_vuetify`.
"""

from glue.config import viewer_tool
from glue.plugins.tools.path_slicer.matplotlib_mode import (
    BasePathSlicerCrosshairMode, BasePathSlicerMode)

from glue_jupyter.matplotlib.image import ImageJupyterViewer


__all__ = ['MatplotlibJupyterPathSlicerMode',
           'MatplotlibJupyterPathSlicerCrosshairMode']


@viewer_tool
class MatplotlibJupyterPathSlicerMode(BasePathSlicerMode):
    tool_id = 'jupyter:slice'
    slice_viewer_cls = ImageJupyterViewer


@viewer_tool
class MatplotlibJupyterPathSlicerCrosshairMode(BasePathSlicerCrosshairMode):
    tool_id = 'jupyter:path_crosshair'
