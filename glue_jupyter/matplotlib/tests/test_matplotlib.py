import os
import sys
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

DATA = os.path.join(os.path.dirname(__file__), 'data')


def test_matplotlib():

    with open(os.path.join(DATA, 'matplotlib.ipynb')) as f:
        nb = nbformat.read(f, as_version=4)

    if sys.version_info[0] < 3:
        kernel_name = 'python2'
    else:
        kernel_name = 'python3'

    ep = ExecutePreprocessor(timeout=600, kernel_name=kernel_name)
    ep.preprocess(nb, {'metadata': {'path': DATA}})
