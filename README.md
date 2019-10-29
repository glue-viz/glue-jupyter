# Jupyter interface for Glue

Sometimes known as "Glupyter"

[![Build Status](https://dev.azure.com/glue-viz/glue-jupyter/_apis/build/status/glue-viz.glue-jupyter?branchName=master)](https://dev.azure.com/glue-viz/glue-jupyter/_build/latest?definitionId=7&branchName=master)

### About

[Glue](http://glueviz.org/) is a Python library to explore relationships within and among datasets. The main interface until now has been based on [Qt](https://www.qt.io), but the **glue-jupyter** package aims to provide a way to use Glue in Jupyter notebooks and Jupyter lab instead. This is currently a work in progress and highly experimental.

For some notebooks with examples of usage of glue-jupyter, see the ``notebooks`` directory.

You can try out glue-jupyter online at mybinder:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/glue-viz/glue-jupyter/master?filepath=notebooks)

Notebooks with real data:

* [Investigating star formation in the W5 region](https://mybinder.org/v2/gh/glue-viz/glue-jupyter/master?filepath=notebooks%2FAstronomy%2FW5%2FW5%20Tutorial.ipynb) (example with linking a table and an image)
* [Exploring the L1448 data in 3D](https://mybinder.org/v2/gh/glue-viz/glue-jupyter/master?filepath=notebooks%2FAstronomy%2FL1448%2FL1448%20in%203D.ipynb) (example of 3D volume rendering)
* [Visualizing flight paths in the Boston area](https://mybinder.org/v2/gh/glue-viz/glue-jupyter/master?filepath=notebooks%2FPlanes%2FBoston%20Planes.ipynb) (example with a single tabular dataset)
* [Distance to the Pleiades with GAIA data](https://mybinder.org/v2/gh/glue-viz/glue-jupyter/master?filepath=notebooks%2FAstronomy%2FGAIA%2FDistance%20to%20The%20Pleiades%20with%20Glupyter%20and%20Gaia%20DR2.ipynb)



### Installing

For now, installing should be done using pip:

    pip install git+https://github.com/glue-viz/glue-jupyter.git

Or from source:

    git clone https://github.com/glue-viz/glue-jupyter.git
    cd glue-jupyter
    pip install -e .

### Testing

The test suite can be run using:

    pytest glue_jupyter
