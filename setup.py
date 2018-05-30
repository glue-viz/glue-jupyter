import os
import imp
from setuptools import setup

dirname = os.path.dirname(__file__)
path_version = os.path.join(dirname, 'glue_jupyter/_version.py')
version = imp.load_source('version', path_version)

name        = 'glue-jupyter'
author      = 'Maarten A. Breddels'
author_email= 'maartenbreddels@gmail.com'
license     = 'BSD License'
version     = version.__version__
url         = 'https://glueviz.org'
install_requires = ['glueviz', 'ipyvolume', 'bqplot', 'ipympl']

extra_requires = {
      'test': ['pytest-mock']
}
setup(name=name,
      version=version,
      description='Jupyter notebook/lab viewers for glue',
      url=url,
      author=author,
      author_email=author_email,
      install_requires=install_requires,
      license=license,
      packages=[name.replace('-', '_')],
      zip_safe=False
      )
