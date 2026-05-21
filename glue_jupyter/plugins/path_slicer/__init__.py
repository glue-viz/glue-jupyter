"""
Path slicer plugin for glue-jupyter. Loaded via the ``glue.plugins``
entry point (see ``pyproject.toml``); :func:`setup` is invoked from
:func:`glue.main.load_plugins` and registers the bqplot and matplotlib
tool IDs on the image viewers.
"""


def setup():
    # Imports are deferred to setup() so importing this package doesn't
    # eagerly drag in the matplotlib + bqplot stacks before glue's
    # plugin loader is ready.
    from glue_jupyter.bqplot.image import BqplotImageView  # noqa: PLC0415
    from glue_jupyter.matplotlib.image import ImageJupyterViewer  # noqa: PLC0415

    # Importing the tool modules runs @viewer_tool decorators that
    # register the classes with glue's global tool registry.
    from .matplotlib import (MatplotlibJupyterPathSlicerMode,  # noqa: F401, PLC0415
                             MatplotlibJupyterPathSlicerCrosshairMode)
    from .bqplot import (BqplotPathSlicerMode,  # noqa: F401, PLC0415
                         BqplotPathSlicerCrosshairMode)

    for tool_id in ('jupyter:slice', 'jupyter:path_crosshair'):
        if tool_id not in ImageJupyterViewer.tools:
            ImageJupyterViewer.tools.append(tool_id)

    for tool_id in ('bqplot:slice', 'bqplot:path_crosshair'):
        if tool_id not in BqplotImageView.tools:
            BqplotImageView.tools.append(tool_id)
