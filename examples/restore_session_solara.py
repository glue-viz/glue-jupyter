"""
Restore a Qt glue session as a Solara dashboard.

Usage:
    solara run examples/restore_session_solara.py

This demonstrates that the session patching infrastructure in
glue_jupyter.session can be reused directly for glue-solara, since
glue-solara builds on top of glue-jupyter viewers.

Note: vispy 3D viewers are excluded as they require OpenGL which is
not available in the solara server context.
"""
from pathlib import Path

import solara
from glue_jupyter.app import JupyterApplication
from glue_solara.app import GlueApp

SESSION_PATH = str(Path(__file__).parent.parent / "glue_jupyter" / "tests" / "data" / "qt_session.glu")

EXCLUDE_VIEWER_TYPES = {
    "glue_vispy_viewers.scatter.jupyter.scatter_viewer.JupyterVispyScatterViewer",
    "glue_vispy_viewers.volume.jupyter.volume_viewer.JupyterVispyVolumeViewer",
}


@solara.component
def Page():
    def create_app():
        return JupyterApplication.restore_session(
            SESSION_PATH, exclude_viewer_types=EXCLUDE_VIEWER_TYPES, widget_2d='matplotlib')

    app = solara.use_memo(create_app, [])
    GlueApp(app)
