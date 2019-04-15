Getting started
===============

To start using glue in the Jupyter notebook or Jupyter lab, you will need to
call the :func:`~glue_jupyter.jglue` function::

    >>> from glue_jupyter import jglue
    >>> app = jglue()

This will automatically set up a data container (called a *data collection* in
glue) and the ``app`` object can then be used to load data, link data, and
create visualizations. For instance, suppose that you have a CSV file that you
want to visualize. Start off by loading it with::

    >>> table = app.load_data('mytable.csv')

The ``table`` variable points to a glue `~glue.core.data.Data` object. For more
information about how to work with and extract values from this kind of object
see `this tutorial <http://docs.glueviz.org/en/stable/python_guide/data_tutorial.html>`__
in the main glue documentation.

You can then create visualizations using methods on ``app`` - for example, to
create a histogram visualization, use `~glue_jupyter.JupyterApplication.histogram1d`::

    >>> histogram = app.histogram1d(data=table)

for a 2-d scatter plot, use `~glue_jupyter.JupyterApplication.scatter2d`::

    >>> scatter2d = app.scatter2d(data=table)

and for a 3-d scatter plot, use `~glue_jupyter.JupyterApplication.scatter3d`::

    >>> scatter3d = app.scatter3d(data=table)

Other available visualizations include
`~glue_jupyter.JupyterApplication.profile1d`,
`~glue_jupyter.JupyterApplication.imshow`, and
`~glue_jupyter.JupyterApplication.volshow`.

.. TODO: continue writing this page!
