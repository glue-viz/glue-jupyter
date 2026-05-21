"""
Lightweight ``ipywidgets.Dropdown`` helper that lets a path slicer
tool's user pick the next-trace target without going through any
backend-specific menu.

The dropdown options come from ``tool.menu_entries()`` and the
selected value flows back into ``tool.set_target()``. The vuetify
toolbar in glue-jupyter doesn't natively support dropdowns next to
toolbar buttons, so the widget is just exposed as ``tool.target_dropdown``
for the notebook author to display where they like.
"""
import ipywidgets


__all__ = ['JupyterTargetDropdownMixin']


class JupyterTargetDropdownMixin:
    """
    Mixin for path slicer tools (matplotlib and bqplot variants) that
    expose ``menu_entries()`` / ``set_target()`` / ``_target_trace``.
    Provides ``self.target_dropdown`` and keeps it in sync with the
    tool's traces via the ``_on_traces_changed`` hook.
    """

    def _init_target_dropdown(self):
        self._dropdown = ipywidgets.Dropdown(
            options=self.menu_entries(),
            value=self._target_trace,
            description='Target:')
        self._dropdown.observe(self._on_dropdown_change, names='value')

    @property
    def target_dropdown(self):
        """The :class:`ipywidgets.Dropdown` widget. Display it in a
        notebook with ``IPython.display.display(tool.target_dropdown)``
        or compose it into a custom layout."""
        return self._dropdown

    @property
    def companion_widget(self):
        """:class:`IPyWidgetView` reads this attribute on each tool
        when assembling :attr:`~IPyWidgetView.toolbar_selection_tools`,
        so the dropdown shows up inline next to the toolbar buttons."""
        return self._dropdown

    def _on_dropdown_change(self, change):
        self.set_target(change['new'])

    def _on_traces_changed(self):
        # Rebuild options after a trace was added; reflect the
        # committed target in the widget without feedback.
        self._dropdown.unobserve(self._on_dropdown_change, names='value')
        self._dropdown.options = self.menu_entries()
        self._dropdown.value = self._target_trace
        self._dropdown.observe(self._on_dropdown_change, names='value')
