import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

DATA = os.path.join(os.path.dirname(__file__), 'data')


def test_notebook():

    # Run an actual notebook

    with open(os.path.join(DATA, 'matplotlib.ipynb')) as f:
        nb = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    ep.preprocess(nb, {'metadata': {'path': DATA}})
