# This is an image sub-class that automatically gets its values from an object
# that implements __call__ with a bounds= argument and returns a fixed
# resolution buffer (FRB). It is the equivalent of FRBArtist in glue-core.

import numpy as np

from bqplot import ColorScale
from bqplot_image_gl import ImageGL

from ...utils import debounced

__all__ = ['FRBImage']

EMPTY_IMAGE = np.zeros((10, 10, 4), dtype=np.uint8)


class FRBImage(ImageGL):

    def __init__(self, viewer, array_maker):

        # FIXME: need to use weakref to avoid circular references
        self.viewer = viewer

        self.scale_image = ColorScale()
        self.scales = {'x': self.viewer.scale_x,
                       'y': self.viewer.scale_y,
                       'image': self.scale_image}

        super().__init__(image=EMPTY_IMAGE, scales=self.scales)

        self.array_maker = array_maker

        self.viewer.figure.axes[0].scale.observe(self.debounced_update, 'min')
        self.viewer.figure.axes[0].scale.observe(self.debounced_update, 'max')
        self.viewer.figure.axes[1].scale.observe(self.debounced_update, 'min')
        self.viewer.figure.axes[1].scale.observe(self.debounced_update, 'max')

        self.update()

    @debounced(method=True)
    def debounced_update(self, *args, **kwargs):
        return self.update(self, *args, **kwargs)

    def update(self, *args, **kwargs):

        # Get current limits from the plot
        xmin = self.viewer.figure.axes[0].scale.min
        xmax = self.viewer.figure.axes[0].scale.max
        ymin = self.viewer.figure.axes[1].scale.min
        ymax = self.viewer.figure.axes[1].scale.max

        if xmin is None or xmax is None or ymin is None or ymax is None:
            return

        # Find out the size of the widget. Unfortunately there is actually
        # no way to find this out, so we need to hard-code this, and we could
        # make it a parameter in future. Bqplot does allow us to constrain the
        # aspect ratio though so we could envisage trying to use that info
        # to make sure the ratio of the sizes is sensible..
        ny, nx = 256, 256

        # Set up bounds
        bounds = [(ymin, ymax, ny), (xmin, xmax, nx)]

        # Get the array and assign it to the artist
        image = self.array_maker(bounds=bounds)
        if image is not None:
            with self.hold_sync():
                self.image = image
                self.x = (xmin, xmax)
                self.y = (ymin, ymax)
        else:
            self.image = EMPTY_IMAGE

    def invalidate_cache(self):
        self.update()
