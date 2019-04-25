Installation
============

To install the latest developer version of the **glue-jupyter** package as
well as its dependencies, you will need the latest developer version of some
dependencies, including glue itself. If you are using conda, we therefore
recommend that you create a new environment::

    conda create -n glue-jupyter python=3.7

To install glue-jupyter along with all its dependencies, you can do::

    pip install git+https://github.com/glue-viz/glue-jupyter

If you are interested in using glue-jupyter in Jupyter Lab, you will need to
also install the following extensions manually::

    jupyter labextension install @jupyter-widgets/jupyterlab-manager \
                                 ipyvolume jupyter-threejs jupyter-materialui

as well as the following developer versions of Jupyter lab extensions::

    git clone --branch scatter_webgl https://github.com/maartenbreddels/bqplot/
    jupyter labextension install bqplot/js

    git clone https://github.com/glue-viz/ipyastroimage/
    jupyter labextension install ipyastroimage/js
