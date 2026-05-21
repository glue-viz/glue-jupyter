"""
glue-jupyter wrapper around glue-core's matplotlib path slicer modes.
The multi-trace data model and matplotlib path overlays live in
:mod:`glue.plugins.tools.path_slicer.matplotlib_mode`; this module
adds the Jupyter image viewer class and an ``ipywidgets.Dropdown``
that lets the user pick the next-trace target.
"""

from glue.config import viewer_tool
from glue.plugins.tools.path_slicer.matplotlib_mode import (
    BasePathSlicerCrosshairMode, BasePathSlicerMode)

from glue_jupyter.matplotlib.image import ImageJupyterViewer

from ._dropdown import JupyterTargetDropdownMixin


__all__ = ['MatplotlibJupyterPathSlicerMode',
           'MatplotlibJupyterPathSlicerCrosshairMode']


@viewer_tool
class MatplotlibJupyterPathSlicerMode(JupyterTargetDropdownMixin,
                                      BasePathSlicerMode):
    tool_id = 'jupyter:slice'
    slice_viewer_cls = ImageJupyterViewer

    def __init__(self, viewer, **kwargs):
        super().__init__(viewer, **kwargs)
        self._init_target_dropdown()


@viewer_tool
class MatplotlibJupyterPathSlicerCrosshairMode(BasePathSlicerCrosshairMode):
    tool_id = 'jupyter:path_crosshair'
