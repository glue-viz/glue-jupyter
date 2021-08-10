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

        # NOTE: we deliberately don't call .update() here because when FRBImage
        # is created for the main composite image layer the composite arrays
        # haven't been set up yet, and for subset layers the layer gets force
        # updated anyway when the layers are added to the viewer.

    @debounced(method=True)
    def debounced_update(self, *args, **kwargs):
        return self.update(self, *args, **kwargs)

    @property
    def shape(self):
        return self.viewer.shape

    def update(self, *args, **kwargs):

        if self.shape is None:
            return

        # Get current limits from the plot
        xmin = self.viewer.figure.axes[0].scale.min
        xmax = self.viewer.figure.axes[0].scale.max
        ymin = self.viewer.figure.axes[1].scale.min
        ymax = self.viewer.figure.axes[1].scale.max

        if xmin is None or xmax is None or ymin is None or ymax is None:
            return

        ny, nx = self.shape

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
