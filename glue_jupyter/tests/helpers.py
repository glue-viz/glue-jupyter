from functools import wraps

import matplotlib.pyplot as plt
import pytest
from IPython.display import display
from PIL import Image

__all__ = ['visual_widget_test']


def visual_widget_test(*args, **kwargs):

    tolerance = kwargs.pop("tolerance", 0)
    style = kwargs.pop("style", {})
    savefig_kwargs = kwargs.pop("savefig_kwargs", {})
    savefig_kwargs["metadata"] = {"Software": None}
    savefig_kwargs["dpi"] = 100

    def decorator(test_function):
        @pytest.mark.mpl_image_compare(
            tolerance=tolerance, style=style, savefig_kwargs=savefig_kwargs, **kwargs
        )
        @wraps(test_function)
        def test_wrapper(tmp_path, page_session,
*args, **kwargs):
            layout = test_function(tmp_path, page_session,
*args, **kwargs)

            layout.add_class("test-viewer")
            layout.layout = {"width": "800px", "height": "600px"}

            display(layout)

            viewer = page_session.locator(".test-viewer")
            viewer.wait_for()

            screenshot = viewer.screenshot()

            with open(tmp_path / "screenshot.png", "wb") as f:
                f.write(screenshot)

            image = Image.open(tmp_path / "screenshot.png")
            size_x, size_y = image.size

            fig = plt.figure(figsize=(size_x / 100, size_y / 100))
            ax = fig.add_axes([0, 0, 1, 1])
            ax.imshow(image)
            plt.axis("off")

            return fig

        return test_wrapper

    # If the decorator was used without any arguments, the only positional
    # argument will be the test to decorate so we do the following:
    if len(args) == 1:
        return decorator(*args)

    return decorator
