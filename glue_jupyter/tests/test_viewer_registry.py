from glue_jupyter.registries import viewer_registry
from glue.viewers.common.viewer import Viewer
import glue_jupyter as gj

from .data_viewer_test import ExternalViewerTest # noqa


def test_add_client():
    @viewer_registry("test")
    class ClientTest(object):
        pass

    assert viewer_registry.members['test']['cls'] == ClientTest


def test_adding_viewers():

    @viewer_registry("test2")
    class ViewerTest(Viewer):
        pass

    app = gj.jglue()

    from glue_jupyter.table import TableViewer
    viewer_cls = TableViewer

    s1 = app.new_data_viewer(viewer_cls, data=None)
    assert len(app.viewers) == 1
    assert app.viewers[0] is s1

    s2 = app.new_data_viewer('test2', data=None, show=False)
    assert len(app.viewers) == 2
    assert app.viewers[1] is s2
    assert isinstance(s2, ViewerTest)


def test_external_viewer():
    app = gj.jglue()
    s = app.new_data_viewer('externalviewer', data=None, show=False)
    assert len(app.viewers) == 1
    assert app.viewers[0] is s
