#!/bin/bash

set -ex

# Keep git happy

git config --global user.email "binder@binder.com"
git config --global user.name "Binder"

# Install glue-jupyter and all requirements as well as Jupyter Lab. Also
# install astroquery for the GAIA notebook.

pip install . jupyterlab astroquery --user
