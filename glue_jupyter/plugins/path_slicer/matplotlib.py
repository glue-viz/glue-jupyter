"""
glue-jupyter wrapper around glue-core's matplotlib path slicer modes.
The interactive behaviour lives in
:mod:`glue.plugins.tools.path_slicer.matplotlib_mode`; this module just
subclasses with the Jupyter image viewer class and registers the tool
IDs.
"""

from glue.config import viewer_tool
from glue.plugins.tools.path_slicer.matplotlib_mode import (
    BasePathSlicerMode, BasePathSlicerCrosshairMode)

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
