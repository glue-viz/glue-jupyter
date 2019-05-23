Notes for developers
====================

Understanding how the viewers are written
-----------------------------------------

Glue provides a standard infrastructure for developing custom viewers, which
follows a common pattern regardless of whether these viewers are for the
Jupyter platform, Qt, or other front-ends. This infrastructure is described in
detail in :ref:`glue:state-viewer`, and the different viewers here follow these
guidelines.

Linking custom widgets with glue state objects
----------------------------------------------

If you are interested in developing additional functionality for Jupyter that
interacts with glue, for example by extending the available viewers, or
interacting with the data object or the links, you can easily do so.

As described in :doc:`getting_started`, each viewer and viewer layer has an
associated state object, where a state object is a collection of properties.
These properties can have callbacks assigned to them which get called when the
properties change (see :ref:`glue:state-viewer` for more details).

The `ipywidgets <https://ipywidgets.readthedocs.io/en/stable/>`_ package makes
use of `traitlets <https://traitlets.readthedocs.io/en/stable/>`_ which provides
similar functionality (although glue state objects are unrelated to traitlets).
We provide convenience functions to link properties of state objects with
traits on e.g. widgets. The :func:`~glue_jupyter.link.dlink` function can be
used to create a directional link where a change in the first property results
in the second property being updated::

    from glue_jupyter.link import dlink
    dlink((state, 'visible'), (widget, 'visible'))

and the :func:`~glue_jupyter.link.link` function can be used to create a
bi-directional link, where the two properties are kept in sync::

    from glue_jupyter.link import link
    dlink((state, 'color'), (widget, 'color'))

Accessing individual parts of viewers
-------------------------------------

By default, the data viewers will be shown using a pre-configured layout, with
the figure on the left, and the viewer and layer options on the right in tabs.
The selection tools, active subset, and selection mode are shown above.
However, developers can choose to override this layout. The main individual
widgets that make up a data viewer can be accessed using the following
properties on a viewer object:

* `~glue_jupyter.view.IPyWidgetView.toolbar_selection_tools`: the basic
  selection tools (e.g. the rectangular, circular, or lasso selection tools).

* `~glue_jupyter.view.IPyWidgetView.toolbar_active_subset`: the drop-down
  menu with the current active subset.

* `~glue_jupyter.view.IPyWidgetView.toolbar_selection_mode`: the toolbar to
  select the logical subset selection mode.

* `~glue_jupyter.view.IPyWidgetView.figure_widget`: the main widget containing
  the figure.

* `~glue_jupyter.view.IPyWidgetView.viewer_options`: the collection of
  widgets used to control the general viewer options.

* `~glue_jupyter.view.IPyWidgetView.layer_options`: a widget that combines
  a way to select the current layer being edited, and the widgets to control
  the options for that layer.

* `~glue_jupyter.view.IPyWidgetView.output_widget`: a widget containing textual
  output such as errors, etc.

To override the layout, define a function that takes a viewer and returns
a widget containing the layout that you want, for example::

    from ipywidgets import VBox

    def simple_viewer_layout(viewer):
        return VBox([viewer.toolbar_selection_tools, viewer.figure_widget])

then register it using::

    from glue_jupyter import set_layout_factory

    set_layout_factory(simple_viewer_layout)

Interacting with other glue objects
-----------------------------------

You can also create custom widgets to interact with the main data collection,
data objects, subsets, links, and many other parts of glue. See the following
detailed tutorials to find out about the programmatic API for various key
components of glue:

* :ref:`glue:data_tutorial` - for the data collection, data, and subsets
* :ref:`glue:linking-framework` - for the data linking framework
* :ref:`glue:communication` - for the event framework
