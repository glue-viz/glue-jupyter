from mimetypes import guess_type
import os
import ipyvuetify as v
import traitlets
import base64

from glue.core.callback_property import add_callback

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
        ext = os.path.splitext(tool.icon)[1][1:] or "svg"
        if os.path.exists(tool.icon):
            path = tool.icon
        else:
            path = icon_path(tool.icon, icon_format=ext)

        format = guess_type(path)[0]
        image_prefix = "image/"
        if format is None or not format.startswith(image_prefix):
            raise ValueError(f"Invalid or unknown image MIME type for: {path}")
        format = format[len(image_prefix):]
        base_entry = {'tooltip': tool.tool_tip, 'img': read_icon(path, format)}

        def _menu_payload():
            """Snapshot of the tool's current menu state, or an empty
            dict if the tool doesn't have a menu."""
            if not hasattr(tool, 'menu_entries'):
                return {}
            entries = tool.menu_entries()
            target = getattr(tool, '_target_trace', None)
            return {
                'menu_labels': [label for label, _ in entries],
                'menu_active_index': next(
                    (i for i, (_, t) in enumerate(entries) if t is target),
                    0),
            }

        def _entry():
            return {**base_entry, **_menu_payload()}

        # Show/hide the button by adding/removing the entry from
        # tools_data as ``tool.enabled`` changes. Apply the current
        # value immediately so a tool that set ``enabled = False`` in
        # its __init__ is hidden from the start.
        def _set_visible(state):
            if state:
                self.tools_data = {**self.tools_data, tool.tool_id: _entry()}
            else:
                new = dict(self.tools_data)
                new.pop(tool.tool_id, None)
                self.tools_data = new

        add_callback(tool, 'enabled', _set_visible)
        _set_visible(tool.enabled)

        # If the tool exposes a menu, register on its menu-change
        # callbacks so the labels and the active checkmark stay in
        # sync with the tool's state (e.g. each new trace adds an
        # "Update path N" entry).
        if hasattr(tool, '_menu_change_callbacks'):
            def _refresh_menu():
                if tool.tool_id not in self.tools_data:
                    return
                self.tools_data = {**self.tools_data, tool.tool_id: _entry()}
            tool._menu_change_callbacks.append(_refresh_menu)

    def vue_select_menu_item(self, data):
        """Called from the Vue template when a user clicks a menu item
        on a tool button. ``data`` carries ``tool_id`` and ``index``
        (0-based into ``tool.menu_entries()``). Sets the tool's target
        and activates the tool (the icon button isn't a v-btn-toggle
        member, so activation has to be driven explicitly here)."""
        tool_id = data.get('tool_id')
        index = data.get('index')
        tool = self.tools.get(tool_id)
        if tool is None or not hasattr(tool, 'menu_entries'):
            return
        entries = tool.menu_entries()
        if not isinstance(index, int) or not 0 <= index < len(entries):
            return
        _, target = entries[index]
        tool.set_target(target)
        self.active_tool_id = tool_id
