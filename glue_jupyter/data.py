from urllib.request import urlretrieve

__all__ = ['require_data']

DATA_REPO = "https://raw.githubusercontent.com/glue-viz/glue-example-data/master/"


def require_data(file_path):
    """
    Download the specified file to the current folder, preserving the directory
    structure.

    Note that this should include forward slashes for paths even on Windows.
    """

    # For now, this is a simple implementation using urlretrieve, but in future
    # we could always extend it to allow using e.g. wget.

    local_path = file_path.split('/')[-1]

    urlretrieve(DATA_REPO + file_path, local_path)

    print("Successfully downloaded data file to {0}".format(local_path))
