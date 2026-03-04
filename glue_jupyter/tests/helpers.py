from functools import wraps

import pytest
from IPython.display import display

try:
    import solara  # noqa
    import playwright  # noqa
    import pytest_mpl  # noqa
    import pytest_playwright  # noqa
except ImportError:
    HAS_VISUAL_TEST_DEPS = False
else:
    HAS_VISUAL_TEST_DEPS = True

__all__ = ['visual_widget_test', 'visual_ui_test']


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
        @pytest.mark.skipif("not HAS_VISUAL_TEST_DEPS")
        @pytest.mark.mpl_image_compare(
            tolerance=tolerance, **kwargs
        )
        @wraps(test_function)
        def test_wrapper(tmp_path, page_session, *args, **kwargs):
            layout = test_function(tmp_path, page_session, *args, **kwargs)

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


def visual_ui_test(*args, **kwargs):
    """
    Decorator for UI visual regression tests using pytest-mpl.

    The decorated test function should return the screenshot bytes from
    a Playwright element (e.g., `plot.screenshot()`).

    This is similar to visual_widget_test but for tests that handle
    their own screenshot capture.
    """
    tolerance = kwargs.pop("tolerance", 0)

    def decorator(test_function):
        @pytest.mark.skipif("not HAS_VISUAL_TEST_DEPS")
        @pytest.mark.mpl_image_compare(tolerance=tolerance, **kwargs)
        @wraps(test_function)
        def test_wrapper(*args, **kwargs):
            screenshot = test_function(*args, **kwargs)
            return DummyFigure(screenshot)

        return test_wrapper

    # If the decorator was used without any arguments, the only positional
    # argument will be the test to decorate so we do the following:
    if len(args) == 1:
        return decorator(*args)

    return decorator
