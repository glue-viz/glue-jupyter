from glue.config import viewer_tool
from glue.viewers.common.tool import SimpleToolMenu


@viewer_tool
class SaveTool(SimpleToolMenu):
    """
    A generic 'save/export' tool that plugins can register new save/export tools
    with.

    To register a new save/export option, add an entry to the viewer
    ``subtools['save']`` list.
    """
    tool_id = 'save'
    icon = 'glue_filesave'
    tool_tip = 'Save/export the plot'
