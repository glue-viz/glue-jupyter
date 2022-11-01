Getting started
===============

Starting up the application
---------------------------

To start using glue in the Jupyter notebook or Jupyter lab, you will need to
call the :func:`~glue_jupyter.jglue` function::

    >>> from glue_jupyter import jglue
    >>> app = jglue()

This will automatically set up a data container (called a *data collection* in
glue) and the ``app`` object can then be used to load data, link data, and
create visualizations.

Loading data
------------

For instance, suppose that you have a CSV file that you
want to visualize. Start off by loading it with::

    >>> table = app.load_data('mytable.csv')

The ``table`` variable points to a glue `~glue.core.data.Data` object. You can
print out a description of the dataset using::

    >>> print(table)
    Data Set: w5_psc
    Number of dimensions: 1
    Shape: 17771
    Main components:
     - ID
     - RAJ2000 [deg]
     - DEJ2000 [deg]
     - Jmag [mag]
     - Hmag [mag]
     - Ksmag [mag]
     - Type
    Coordinate components:
     - Pixel Axis 0 [x]
     - World 0

This shows that the table has seven main columns (or 'components'). The
'Coordinate components' are essentially indexes for the table and can be ignored
for now. To access a particular columns, you can use the indexing notation::

    >>> table['RAJ2000']
    array([41.081526, 41.09856 , 41.100737, ..., 46.015912, 46.022295,
           46.039649])

You can also find out more about how to work with and extract values from glue
`~glue.core.data.Data` objects, as well as creating selections/subsets of data
programmatically in
`this tutorial <http://docs.glueviz.org/en/stable/python_guide/data_tutorial.html>`__
in the main glue documentation.

Creating visualizations
-----------------------

You can then create visualizations using methods on ``app`` - for example, to
create a histogram visualization, use `~glue_jupyter.JupyterApplication.histogram1d`::

    >>> histogram = app.histogram1d(data=table)

for a 2-d scatter plot, use `~glue_jupyter.JupyterApplication.scatter2d`::

    >>> scatter2d = app.scatter2d(data=table)

and for a 3-d scatter plot, use `~glue_jupyter.JupyterApplication.scatter3d`::

    >>> scatter3d = app.scatter3d(data=table)

Other available visualizations include
:`~glue_jupyter.JupyterApplication.profile1d` for collapsing n-dimensional
datasets down to one dimension, `~glue_jupyter.JupyterApplication.imshow` for
images (including image slices through n-dimensional datasets), and
`~glue_jupyter.JupyterApplication.volshow` for volume renderings.

Creating and accessing subsets
------------------------------

To create subsets, click on one of the icons above the image viewer (typically
these icons are blue shapes). You will then be able to click and drag in the
image viewer to defined a subset. The drop-down menu to the right of the
selection tools can be used to determine whether to create a new subset or
change an existing one.

Once you have created one or more subsets, you can access them programmatically
with::

    >>> subset = table.subsets[0]  # access the first subset

and you can e.g. convert this to a boolean mask::

    >>> subset.to_mask()
    array([ True,  True,  True, ...,  True,  True,  True])

or you can also retrieve the subset of values for a given column/attribute::

    >>> subset['RAJ2000']
    array([41.081526, 41.09856 , 41.100737, ..., 46.015912, 46.022295,
           46.039649])

Modifying viewers and layers programmatically
---------------------------------------------

Each viewer has an associated 'state' which is an object with properties that
can be used to control the appearance and contents of the viewer. The state is
accessible via the ``.state`` attribute::

    >>> histogram.state
    <glue.viewers.histogram.state.HistogramViewerState object at 0x7f9714b25c50>

For example, if you are using a 2D scatter viewer, you can change the attribute
shown on the x-axis using::

    >>> histogram.state.x_att = table.id['RAJ2000']

You will notice that we specified ``table.id['RAJ2000']`` rather than
``table.id['RAJ2000']`` as the former is the identifier for the column rather
than the actual values (which the former will return).

Each viewer/visualization contains 'layers', where a layer is for example
the points corresponding to a given dataset or a subset.
We can find a complete list of layers with::

    >>> histogram.state.layers
    [HistogramLayerState for w5_psc, HistogramLayerState for Jmag > 5]

In this example, there are two layers - one for the main dataset, and one for a
subset of the data. We can access the first layer with::

    >>> layer_state = histogram.state.layers[0]

and the layer itself then has properties that can be changed, such as the
color of the points (this is a property that is specific to the layer, not
an overall property of the viewer)::

    >>> layer_state.color = 'blue'
    >>> layer_state.alpha = 0.5

In the following table, you can click on the name of one of the state classes
to find out the complete list of viewer properties that can be changed for the
viewer state objects and the layer state objects. Note that in some viewers,
the subset state is different from the main data state:

=================== ========================= ======================= ========================
Viewer              Viewer state              Data layer state        Subset layer state
=================== ========================= ======================= ========================
|histogram_viewer|  |histogram_viewer_state|  |histogram_layer_state| |histogram_layer_state|
|profile_viewer|    |profile_viewer_state|    |profile_layer_state|   |profile_layer_state|
|scatter_viewer|    |scatter_viewer_state|    |scatter_layer_state|   |scatter_layer_state|
|image_viewer|      |image_viewer_state|      |image_data_state|      |image_subset_state|
|scatter3d_viewer|  |scatter3d_viewer_state|  |scatter3d_layer_state| |scatter3d_layer_state|
|volume_viewer|     |volume_viewer_state|     |volume_layer_state|    |volume_layer_state|
=================== ========================= ======================= ========================

.. |histogram_viewer| replace:: :meth:`~glue_jupyter.JupyterApplication.histogram1d`
.. |histogram_viewer_state| replace:: :class:`~glue.viewers.histogram.state.HistogramViewerState`
.. |histogram_layer_state| replace:: :class:`~glue.viewers.histogram.state.HistogramLayerState`

.. |profile_viewer| replace:: :meth:`~glue_jupyter.JupyterApplication.profile1d`
.. |profile_viewer_state| replace:: :class:`~glue.viewers.profile.state.ProfileViewerState`
.. |profile_layer_state| replace:: :class:`~glue.viewers.profile.state.ProfileLayerState`

.. |scatter_viewer| replace:: :meth:`~glue_jupyter.JupyterApplication.scatter2d`
.. |scatter_viewer_state| replace:: :class:`~glue.viewers.scatter.state.ScatterViewerState`
.. |scatter_layer_state| replace:: :class:`~glue.viewers.scatter.state.ScatterLayerState`

.. |image_viewer| replace:: :meth:`~glue_jupyter.JupyterApplication.imshow`
.. |image_viewer_state| replace:: :class:`~glue.viewers.image.state.ImageViewerState`
.. |image_data_state| replace:: :class:`~glue.viewers.image.state.ImageLayerState`
.. |image_subset_state| replace:: :class:`~glue.viewers.image.state.ImageSubsetLayerState`

.. |scatter3d_viewer| replace:: :meth:`~glue_jupyter.JupyterApplication.scatter3d`
.. |scatter3d_viewer_state| replace:: :class:`~glue_jupyter.common.state3d.Scatter3DViewerState`
.. |scatter3d_layer_state| replace:: :class:`~glue_jupyter.ipyvolume.scatter.Scatter3DLayerState`

.. |volume_viewer| replace:: :meth:`~glue_jupyter.JupyterApplication.volshow`
.. |volume_viewer_state| replace:: :class:`~glue_jupyter.common.state3d.VolumeViewerState`
.. |volume_layer_state| replace:: :class:`~glue_jupyter.ipyvolume.volume.VolumeLayerState`
