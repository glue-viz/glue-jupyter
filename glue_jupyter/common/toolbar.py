from __future__ import absolute_import, division, print_function

from ipywidgets import Image
from ipymaterialui import ToggleButtonGroup, ToggleButton

from glue.icons import icon_path

__all__ = ['BasicJupyterToolbar']

ICON_WIDTH = 20


class BasicJupyterToolbar(ToggleButtonGroup):

    def __init__(self):
        super().__init__(exclusive=True, style={'margin': '4px'}, value=None)
        self.tools = {}
        self.observe(self._change_tool, "value")

    def _change_tool(self, event):

        if event['old'] is not None:
            self.tools[event['old']].deactivate()

        if event['new'] is not None:
            self.tools[event['new']].activate()

    def add_tool(self, tool):
        self.tools[tool.tool_id] = tool
        icon = Image.from_file(icon_path(tool.icon, icon_format='svg'),
                               width=ICON_WIDTH)
        button = ToggleButton(children=[icon], value=tool.tool_id)
        if self.children is None:
            self.children = (button,)
        else:
            self.children = tuple(self.children) + (button,)
