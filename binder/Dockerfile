# This dockerfile is used to set up a plain Linux environment into which we can
# install all dependencies with pip, and avoid conda. The documentation about
# using Dockerfiles with mybinder can be found here:

# https://mybinder.readthedocs.io/en/latest/tutorials/dockerfile.html#preparing-your-dockerfile

FROM ubuntu:20.04

# Set up Python 3.6

RUN apt update
RUN apt install -y python3 python3-pip git
RUN pip3 install --upgrade pip

# Set up user as required by mybinder docs:

ENV NB_USER jovyan
ENV NB_UID 1000
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

# Copy the contents of notebooks and the postBuild script into the root of
# the binder environment.

COPY . ${HOME}/
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}

# Change working directory

WORKDIR ${HOME}

# Update variables to point to local install

ENV PATH="${HOME}/.local/bin:${PATH}"
ENV JUPYTER_CONFIG_DIR="${HOME}/.local/etc/jupyter/"

# Run post-build script

RUN binder/setup.sh
