import os
from glue_jupyter.app import JupyterApplication
from glue_jupyter import session  # noqa
DATA = os.path.join(os.path.dirname(__file__), 'data')


def test_qt_to_jupyter_session():

    app = JupyterApplication.restore_session(os.path.join(DATA, 'qt_session.glu'))

    assert len(app.viewers) == 6
