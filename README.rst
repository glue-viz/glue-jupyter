Jupyter interface for Glue
==========================

Sometimes known as “Glupyter”

|Build Status| |Coverage Status| |Documentation Status|

About
~~~~~

`Glue <http://glueviz.org/>`__ is a Python library to explore
relationships within and among datasets. The main interface until now
has been based on `Qt <https://www.qt.io>`__, but the **glue-jupyter**
package aims to provide a way to use Glue in Jupyter notebooks and
Jupyter lab instead. This is currently a work in progress and highly
experimental.

For some notebooks with examples of usage of glue-jupyter, see the
``notebooks`` directory.

You can try out glue-jupyter online at mybinder:

|Binder|

Notebooks with real data:

-  `Investigating star formation in the W5
   region <https://mybinder.org/v2/gh/glue-viz/glue-jupyter/main?urlpath=lab/tree/notebooks%2FAstronomy%2FW5%2FW5%20Tutorial.ipynb>`__
   (example with linking a table and an image)
-  `Exploring the L1448 data in
   3D <https://mybinder.org/v2/gh/glue-viz/glue-jupyter/main?urlpath=lab/tree/notebooks%2FAstronomy%2FL1448%2FL1448%20in%203D.ipynb>`__
   (example of 3D volume rendering)
-  `Visualizing flight paths in the Boston
   area <https://mybinder.org/v2/gh/glue-viz/glue-jupyter/main?urlpath=lab/tree/notebooks%2FPlanes%2FBoston%20Planes.ipynb>`__
   (example with a single tabular dataset)
-  `Distance to the Pleiades with GAIA
   data <https://mybinder.org/v2/gh/glue-viz/glue-jupyter/main?urlpath=lab/tree/notebooks%2FAstronomy%2FGAIA%2FDistance%20to%20The%20Pleiades%20with%20Glupyter%20and%20Gaia%20DR2.ipynb>`__

Installing
~~~~~~~~~~

For now, installing should be done using pip::

   pip install git+https://github.com/glue-viz/glue-jupyter.git

Or from source::

   git clone https://github.com/glue-viz/glue-jupyter.git
   cd glue-jupyter
   pip install -e .

Testing
~~~~~~~

The test suite can be run using::

   pytest glue_jupyter

.. |Build Status| image:: https://github.com/glue-viz/glue-jupyter/actions/workflows/ci_workflows.yml/badge.svg
    :target: https://github.com/glue-viz/glue-jupyter/actions/
    :alt: Glue Jupyter's GitHub Actions CI Status
.. |Coverage Status| image:: https://codecov.io/gh/glue-viz/glue-jupyter/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/glue-viz/glue-jupyter
    :alt: Glue Jupyter's Coverage Status
.. |Documentation Status| image:: https://img.shields.io/readthedocs/glue-jupyter/latest.svg?logo=read%20the%20docs&logoColor=white&label=Docs&version=stable
    :target: https://glue-jupyter.readthedocs.io/en/stable/?badge=stable
    :alt: Glue Jupyter's Documentation Status
.. |Binder| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/glue-viz/glue-jupyter/main?urlpath=lab/tree/notebooks
    :alt: Launch Glue Jupyter on mybinder
