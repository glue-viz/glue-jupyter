# Jupyter interface for Glue

[![Build Status](https://travis-ci.org/glue-viz/glue-jupyter.svg?branch=master)](https://travis-ci.org/glue-viz/glue-jupyter)

### About

[Glue](http://glueviz.org/) is a Python library to explore relationships within and among datasets. The main interface until now has been based on [Qt](https://www.qt.io), but the **glue-jupyter** package aims to provide a way to use Glue in Jupyter notebooks and Jupyter lab instead. This is currently a work in progress and highly experimental.

For some notebooks with examples of usage of glue-jupyter, see the ``notebooks`` directory.

You can try out glue-jupyter online at mybinder:

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/glue-viz/glue-jupyter/mybinder)

Direct links to notebooks
  * [demo_gaussian](https://mybinder.org/v2/gh/glue-viz/glue-jupyter/master?filepath=notebooks%2Fdemo_image.ipynb)
  * [demo_image](https://mybinder.org/v2/gh/glue-viz/glue-jupyter/master?filepath=notebooks%2Fdemo_image.ipynb)

### Installing

For now, installing should be done using pip:

    pip install -e .
    
### Testing

The test suite can be run using:

    pytest glue_jupyter

