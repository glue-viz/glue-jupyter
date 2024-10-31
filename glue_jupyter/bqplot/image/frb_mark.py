# This is an image sub-class that automatically gets its values from an object
# that implements __call__ with a bounds= argument and returns a fixed
# resolution buffer (FRB). It is the equivalent of FRBArtist in glue-core.

import math
import numpy as np

from bqplot import ColorScale
from bqplot_image_gl import ImageGL

from ...utils import debounced

__all__ = ['FRBImage']

EMPTY_IMAGE = np.zeros((10, 10, 4), dtype=np.uint8)


class FRBImage(ImageGL):

    def __init__(self, viewer, array_maker, compression='png'):

        # FIXME: need to use weakref to avoid circular references
        self.viewer = viewer

        self._external_padding = 0

        self.scale_image = ColorScale()
        self.scales = {'x': self.viewer.scale_x,
                       'y': self.viewer.scale_y,
                       'image': self.scale_image}

        super().__init__(image=EMPTY_IMAGE, scales=self.scales, compression=compression)

        self.array_maker = array_maker

        self.viewer.figure.axes[0].scale.observe(self.debounced_update, 'min')
        self.viewer.figure.axes[0].scale.observe(self.debounced_update, 'max')
        self.viewer.figure.axes[1].scale.observe(self.debounced_update, 'min')
        self.viewer.figure.axes[1].scale.observe(self.debounced_update, 'max')

        self._latest_hash = None

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

    @property
    def external_padding(self):
        return self._external_padding

    @external_padding.setter
    def external_padding(self, value):
        previous_value = self._external_padding
        self._external_padding = value
        if value > previous_value:  # no point updating if the value is smaller than before
            self.debounced_update()

    def update(self, *args, force=False, **kwargs):

        # Shape can be (0, 0) when viewer was created and then destroyed.
        if self.shape is None or np.allclose(self.shape, 0):
            return

        # Get current limits from the plot
        xmin = self.viewer.figure.axes[0].scale.min
        xmax = self.viewer.figure.axes[0].scale.max
        ymin = self.viewer.figure.axes[1].scale.min
        ymax = self.viewer.figure.axes[1].scale.max

        if xmin is None or xmax is None or ymin is None or ymax is None:
            return

        current_hash = (xmin, xmax, ymin, ymax, self.external_padding)

        if not force and current_hash == self._latest_hash:
            return

        ny, nx = self.shape

        # Expand beyond the boundary
        if self.external_padding != 0:
            dx = (xmax - xmin)
            dy = (ymax - ymin)
            xmin, xmax = xmin - dx * self.external_padding, xmax + dx * self.external_padding
            ymin, ymax = ymin - dy * self.external_padding, ymax + dy * self.external_padding
            nx *= math.ceil(1 + 2 * self.external_padding)
            ny *= math.ceil(1 + 2 * self.external_padding)

        # Set up bounds
        bounds = [(ymin, ymax, ny), (xmin, xmax, nx)]

        # Get the array and assign it to the artist
        image = self.array_maker(bounds=bounds)
        if image is not None:
            if image.dtype == np.dtype("float64"):
                image = image.astype(np.float32)
            with self.hold_sync():
                self.image = image
                self.x = (xmin, xmax)
                self.y = (ymin, ymax)
        else:
            self.image = EMPTY_IMAGE

        self._latest_hash = current_hash

    def invalidate_cache(self):
        self.update(force=True)
