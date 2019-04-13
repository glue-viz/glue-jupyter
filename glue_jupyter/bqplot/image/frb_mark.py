# This is an image sub-class that automatically gets its values from an object
# that implements __call__ with a bounds= argument and returns a fixed
# resolution buffer (FRB). It is the equivalent of FRBArtist in glue-core.

import numpy as np

from bqplot import ColorScale
from ipyastroimage.astroimage import AstroImage

from ...utils import debounced

__all__ = ['FRBImage']


class FRBImage(AstroImage):

    def __init__(self, viewer, array_maker):

        # FIXME: need to use weakref to avoid circular references
        self.viewer = viewer

        self.scale_image = ColorScale()
        self.scales = {'x': self.viewer.scale_x,
                       'y': self.viewer.scale_y,
                       'image': self.scale_image}

        super().__init__(image=np.zeros((10, 10, 3)), scales=self.scales)

        self.array_maker = array_maker

        self.viewer.figure.axes[0].scale.observe(self.update, 'min')
        self.viewer.figure.axes[0].scale.observe(self.update, 'max')
        self.viewer.figure.axes[1].scale.observe(self.update, 'min')
        self.viewer.figure.axes[1].scale.observe(self.update, 'max')

    @debounced(method=True, wait_for_end=False, delay_seconds=0.1)
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
        ny, nx = 512, 512

        # Set up bounds
        bounds = [(ymin, ymax, ny), (xmin, xmax, nx)]

        # Get the array and assign it to the artist
        with self.hold_sync():
            image = self.array_maker(bounds=bounds)
            if image is None:
                image = np.array([[np.nan]])
            self.image = image
            self.x = (xmin, xmax)
            self.y = (ymin, ymax)

    def invalidate_cache(self):
        self.update()
