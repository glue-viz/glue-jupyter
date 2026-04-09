import os

import pytest

from glue_jupyter.app import JupyterApplication

DATA = os.path.join(os.path.dirname(__file__), 'data')


@pytest.mark.parametrize('widget_2d', ['bqplot', 'matplotlib'])
@pytest.mark.parametrize('widget_3d', ['vispy', 'ipyvolume'])
def test_qt_to_jupyter_session(widget_2d, widget_3d):
    app = JupyterApplication.restore_session(os.path.join(DATA, 'qt_session.glu'),
                                             widget_2d=widget_2d,
                                             widget_3d=widget_3d)
    assert len(app.viewers) == 6
