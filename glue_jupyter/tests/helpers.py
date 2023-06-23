from functools import wraps

import matplotlib.pyplot as plt
import pytest
from IPython.display import display
from PIL import Image

__all__ = ['visual_widget_test']


class DummyFigure:

    def __init__(self, png_bytes):
        self._png_bytes = png_bytes

    def savefig(self, filename_or_fileobj, *args, **kwargs):
        if isinstance(filename_or_fileobj, str):
            with open(filename_or_fileobj, 'wb') as f:
                f.write(self._png_bytes)
        else:
            filename_or_fileobj.write(self._png_bytes)


def visual_widget_test(*args, **kwargs):

    tolerance = kwargs.pop("tolerance", 0)

    def decorator(test_function):
        @pytest.mark.mpl_image_compare(
            tolerance=tolerance, **kwargs
        )
        @wraps(test_function)
        def test_wrapper(tmp_path, page_session,
*args, **kwargs):
            layout = test_function(tmp_path, page_session,
*args, **kwargs)

            layout.add_class("test-viewer")

            display(layout)

            viewer = page_session.locator(".test-viewer")
            viewer.wait_for()

            screenshot = viewer.screenshot()

            return DummyFigure(screenshot)

        return test_wrapper

    # If the decorator was used without any arguments, the only positional
    # argument will be the test to decorate so we do the following:
    if len(args) == 1:
        return decorator(*args)

    return decorator
