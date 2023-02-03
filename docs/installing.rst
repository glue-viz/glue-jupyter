Installation
============

Basic instructions
------------------

The **glue-jupyter** package is currently under active development, and depends
on the latest developer version of several packages. Therefore, we recommend
installing it in an isolated Python environment for now. If you are using conda,
you can create an environment and install the latest version of glue-jupyter in
it using::

    conda create -n glue-jupyter -c glueviz/label/dev python=3.11 glue-jupyter

To switch to the environment, use::

    conda activate glue-jupyter

If you have already installed glue-jupyter as above and want to update it and
all its dependencies, switch to the environment then use::

    conda update -c glueviz/label/dev --all

The above will use conda packages built every day, but may not always include
changes made within the last day. If you want to make sure you have the very
latest version of glue-jupyter, or if you find conda too slow to install all the
dependencies, you can also create the environment with conda (or another Python
environment manager)::

    conda create -n glue-jupyter python=3.11

then switch to the environment as above and install glue-jupyter and all its
dependencies with::

    pip install git+https://github.com/glue-viz/glue-jupyter.git

Jupyter Lab
-----------

If you are interested in using glue-jupyter in Jupyter Lab, you will need to
first install Jupyter Lab (if not already installed)::

    pip install jupyterlab

then install the following extensions manually::

    jupyter labextension install @jupyter-widgets/jupyterlab-manager \
                                 ipyvolume jupyter-threejs \
                                 bqplot bqplot-image-gl jupyter-vuetify
