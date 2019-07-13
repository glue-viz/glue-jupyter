import ipyvuetify as v
from ipywidgets import Image

from glue.icons import icon_path

__all__ = ['BasicJupyterToolbar']

ICON_WIDTH = 20


class BasicJupyterToolbar(v.BtnToggle):

    def __init__(self, viewer):
        super().__init__(v_model='toggle_exclusive', class_='transparent')
        self.tools = {}
        self.on_event('change', self._change_tool)
        self.active = None
        self.output = viewer.output_widget

    def _change_tool(self, widget, event, data):
        with self.output:

            if self.active is not None:
                self.tools[self.active].deactivate()
                self.active = None

            if data:
                self.tools[data].activate()
                self.active = data

    def add_tool(self, tool):
        self.tools[tool.tool_id] = tool
        icon = Image.from_file(icon_path(tool.icon, icon_format='svg'), width=ICON_WIDTH)
        button = v.Btn(slot='activator', icon=True, children=[icon], value=tool.tool_id)
        annotated = v.Tooltip(bottom=True, children=[button, tool.tool_tip])
        self.children = list(self.children) + [annotated]
