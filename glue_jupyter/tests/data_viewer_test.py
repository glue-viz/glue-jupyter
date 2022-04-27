from glue_jupyter.registries import viewer_registry
from glue.viewers.common.viewer import Viewer


@viewer_registry("externalviewer")
class ExternalViewerTest(Viewer):
    pass
