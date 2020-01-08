#!/bin/bash

set -ex

# keep git happy
git config --global user.email "binder@binder.com"
git config --global user.name "Binder"

# Install glue-jupyter and all requirements as well as Jupyter Lab. Also
# install astroquery for the GAIA notebook.

pip install . jupyterlab astroquery --user

# Install Jupyter Lab widgets extensions

jupyter labextension install @jupyter-widgets/jupyterlab-manager \
                             ipyvolume jupyter-threejs jupyter-materialui \
                             bqplot bqplot-image-gl --no-build

# Re-build Jupyter Lab

jupyter lab build
