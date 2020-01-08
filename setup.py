#!/usr/bin/env python

import sys
import setuptools
from distutils.version import LooseVersion
from setuptools import setup

# Setuptools 30.3.0 or later is needed for setup.cfg options to be used
if LooseVersion(setuptools.__version__) < LooseVersion('30.3.0'):
    sys.stderr.write("ERROR: glue-jupyter requires setuptools 30.3.0 or "
                     "later (found {0})".format(setuptools.__version__))
    sys.exit(1)

setup(use_scm_version=True)
