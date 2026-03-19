from ..common.viewer_options_widget import Viewer3DStateWidget

from ...widgets import LinkedDropdown


class Volume3DStateWidget(Viewer3DStateWidget):

    def __init__(self, viewer_state):

        super().__init__(viewer_state)

        self.widget_resolution = LinkedDropdown(self.state,
                                                "resolution",
                                                label="Resolution")

        self.children += (self.widget_resolution,)
