"""
PV slicer plugin for glue-jupyter. Imports register the bqplot and
matplotlib tool variants via ``@viewer_tool`` and append their tool IDs
to the corresponding viewers' tool lists.
"""

from glue_jupyter.bqplot.image import BqplotImageView
from glue_jupyter.matplotlib.image import ImageJupyterViewer

from .matplotlib import (MatplotlibJupyterPathSlicerMode,  # noqa: F401
                         MatplotlibJupyterPathSlicerCrosshairMode)
from .bqplot import (BqplotPathSlicerMode,  # noqa: F401
                     BqplotPathSlicerCrosshairMode)


def _ensure(tool_list, tool_id):
    if tool_id not in tool_list:
        tool_list.append(tool_id)


# Register matplotlib jupyter tools.
_ensure(ImageJupyterViewer.tools, 'jupyter:slice')
_ensure(ImageJupyterViewer.tools, 'jupyter:pv_crosshair')

# Register bqplot tools.
_ensure(BqplotImageView.tools, 'bqplot:slice')
_ensure(BqplotImageView.tools, 'bqplot:pv_crosshair')
