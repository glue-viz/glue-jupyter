# Jupyter interface for Glue

[![Build Status](https://travis-ci.org/glue-viz/glue-jupyter.svg?branch=master)](https://travis-ci.org/glue-viz/glue-jupyter)

### About

[Glue](http://glueviz.org/) is a Python library to explore relationships within and among datasets. The main interface until now has been based on [Qt](https://www.qt.io), but the **glue-jupyter** package aims to provide a way to use Glue in Jupyter notebooks and Jupyter lab instead. This is currently a work in progress and highly experimental.

For some notebooks with examples of usage of glue-jupyter, see the ``notebooks`` directory.

You can try out glue-jupyter online at mybinder:

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/glue-viz/glue-jupyter/mybinder)

Notebooks with real data:

* [Investigating star formation in the W5 region](https://mybinder.org/v2/gh/glue-viz/glue-example-data/jupyter?filepath=Astronomy%2FW5%2FW5%20Tutorial.ipynb) (example with linking a table and an image)
* [Exploring the L1448 data in 3D](https://mybinder.org/v2/gh/glue-viz/glue-example-data/jupyter?filepath=Astronomy%2FL1448%2FL1448%20in%203D.ipynb) (example of 3D volume rendering)
* [Visualizing flight paths in the Boston area](https://mybinder.org/v2/gh/glue-viz/glue-example-data/jupyter?filepath=Planes%2FBoston%20Planes.ipynb) (example with a single tabular dataset)

Notesbooks with generated data:

  * [demo_gaussian](https://mybinder.org/v2/gh/glue-viz/glue-jupyter/master?filepath=notebooks%2Fdemo_image.ipynb)
  * [demo_image](https://mybinder.org/v2/gh/glue-viz/glue-jupyter/master?filepath=notebooks%2Fdemo_image.ipynb)

### Installing

For now, installing should be done using pip:

    pip install -e .
    
### Testing

The test suite can be run using:

    pytest glue_jupyter

