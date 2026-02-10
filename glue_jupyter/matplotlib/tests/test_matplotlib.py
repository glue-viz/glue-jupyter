import os

import pytest

DATA = os.path.join(os.path.dirname(__file__), 'data')


@pytest.mark.notebook
def test_notebook():

    # Run an actual notebook

    import nbformat
    from nbconvert.preprocessors import ExecutePreprocessor

    with open(os.path.join(DATA, 'matplotlib.ipynb')) as f:
        nb = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    ep.preprocess(nb, {'metadata': {'path': DATA}})
