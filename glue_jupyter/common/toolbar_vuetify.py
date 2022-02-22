import os
import ipyvuetify as v
import traitlets
import base64

from glue.icons import icon_path
import glue.viewers.common.tool
from glue.viewers.common.tool import CheckableTool

__all__ = ['BasicJupyterToolbar']

_icons = {}


def read_icon(file_name, format):
    if file_name not in _icons:
        with open(file_name, "rb") as f:
            _icons[file_name] =\
                f'data:image/{format};base64,{base64.b64encode(f.read()).decode("ascii")}'

    return _icons[file_name]


class BasicJupyterToolbar(v.VuetifyTemplate):
    template_file = (__file__, 'basic_jupyter_toolbar.vue')

    active_tool = traitlets.Instance(glue.viewers.common.tool.Tool, allow_none=True,
                                     default_value=None)
    tools_data = traitlets.Dict(default_value={}).tag(sync=True)
    active_tool_id = traitlets.Any().tag(sync=True)

    def __init__(self, viewer):
        self.output = viewer.output_widget
        self.tools = {}
        if viewer._default_mouse_mode_cls is not None:
            self._default_mouse_mode = viewer._default_mouse_mode_cls(viewer)
            self._default_mouse_mode.activate()
        else:
            self._default_mouse_mode = None
        super().__init__()

    @traitlets.observe('active_tool_id')
    def _on_change_v_model(self, change):
        if change.new is not None:
            if isinstance(self.tools[change.new], CheckableTool):
                self.active_tool = self.tools[change.new]
            else:
                # In this case it is a non-checkable tool and we should
                # activate it but not keep the tool checked in the toolbar
                self.tools[change.new].activate()
                self.active_tool_id = None
        else:
            self.active_tool = None

    @traitlets.observe('active_tool')
    def _on_change_active_tool(self, change):
        if change.old:
            change.old.deactivate()
        else:
            if self._default_mouse_mode:
                self._default_mouse_mode.deactivate()
        if change.new:
            change.new.activate()
            self.active_tool_id = change.new.tool_id
        else:
            self.active_tool_id = None
            if self._default_mouse_mode is not None:
                self._default_mouse_mode.activate()

    def add_tool(self, tool):
        self.tools[tool.tool_id] = tool
        # TODO: we should ideally just incorporate this check into icon_path directly.
        if os.path.exists(tool.icon):
            path = tool.icon
        else:
            path = icon_path(tool.icon, icon_format='svg')
        self.tools_data = {
            **self.tools_data,
            tool.tool_id: {
                'tooltip': tool.tool_tip,
                'img': read_icon(path, 'svg+xml')
            }
        }
