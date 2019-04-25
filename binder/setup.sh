#!/bin/bash

set -ex

# keep git happy
git config --global user.email "bin@der.com"
git config --global user.name "Bin Der"

# Install glue-jupyter and all requirements as well as Jupyter Lab. Also
# install astroquery for the GAIA notebook.

pip install . jupyterlab astroquery --user

# Install Jupyter Lab widgets extensions

jupyter labextension install @jupyter-widgets/jupyterlab-manager \
                             ipyvolume jupyter-threejs jupyter-materialui --no-build

git clone --branch scatter_webgl https://github.com/maartenbreddels/bqplot/
jupyter labextension install bqplot/js --no-build

git clone https://github.com/glue-viz/ipyastroimage/
jupyter labextension install ipyastroimage/js --no-build

# Re-build Jupyter Lab

jupyter lab build
