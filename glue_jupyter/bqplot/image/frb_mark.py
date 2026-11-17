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

    @staticmethod
    def _snap_to_lattice(lo, hi, n):
        # Snap an axis range to a power-of-two lattice anchored at the data
        # origin. ``n`` is the number of display-resolution samples requested
        # across ``[lo, hi]``; the returned range is widened outward onto the
        # lattice and the sample count adjusted to match, so the sample
        # positions always fall on the same set of data pixels.
        if n < 2 or hi <= lo:
            return lo, hi, n

        # World separation between adjacent display samples.
        ideal_step = (hi - lo) / (n - 1)

        # Use the largest power-of-two number of data pixels per sample that is
        # still at least as fine as the display (so we never undersample what is
        # shown), but never sample finer than the data grid itself - there is no
        # information below one data pixel and the GPU magnifies for us.
        exponent = max(0, math.floor(math.log2(ideal_step)))
        step = 2.0 ** exponent

        lo_snap = math.floor(lo / step) * step
        hi_snap = math.ceil(hi / step) * step
        n_snap = int(round((hi_snap - lo_snap) / step)) + 1

        return lo_snap, hi_snap, n_snap

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

        ny, nx = self.shape

        # Expand beyond the boundary
        if self.external_padding != 0:
            dx = (xmax - xmin)
            dy = (ymax - ymin)
            xmin, xmax = xmin - dx * self.external_padding, xmax + dx * self.external_padding
            ymin, ymax = ymin - dy * self.external_padding, ymax + dy * self.external_padding
            nx *= math.ceil(1 + 2 * self.external_padding)
            ny *= math.ceil(1 + 2 * self.external_padding)

        # Snap the sampling grid to a dyadic lattice aligned with the reference
        # data pixel grid (the viewer x/y axes are in reference-data pixel
        # coordinates, so one world unit is one data pixel). The FRB samples by
        # nearest-neighbour, so without snapping a pan or zoom of a heavily
        # decimated image lands the sample points on a different set of data
        # pixels each frame, which makes a noisy background flicker. Snapping
        # keeps the sampled data pixels fixed (the texture just translates under
        # the viewport on a pan) and only changes the resolution in factors of
        # two on zoom, so the lattice always refines/coarsens onto itself.
        xmin, xmax, nx = self._snap_to_lattice(xmin, xmax, nx)
        ymin, ymax, ny = self._snap_to_lattice(ymin, ymax, ny)

        current_hash = (xmin, xmax, ymin, ymax, nx, ny, self.external_padding)

        if not force and current_hash == self._latest_hash:
            return

        # Set up bounds
        bounds = [(ymin, ymax, ny), (xmin, xmax, nx)]

        # Get the array and assign it to the artist
        image = self.array_maker(bounds=bounds)
        if image is not None:
            if image.dtype == np.dtype("float64"):
                image = image.astype(np.float32)
            with self.hold_sync():
                self.image = image
                # ImageGL maps the x/y extent across the texture edge-to-edge,
                # but the FRB samples at pixel centres (the linspace endpoints),
                # so the extent has to be expanded by half a sample on each side
                # for the texels to register on the sampled positions. This is
                # also what keeps panning stable: the sample count changes by one
                # as the snapped bounds cross a lattice node, and without the
                # half-sample padding that would shift the whole texture by a
                # sub-pixel amount each time and make the image shimmer.
                half_x = (xmax - xmin) / (nx - 1) / 2 if nx > 1 else 0
                half_y = (ymax - ymin) / (ny - 1) / 2 if ny > 1 else 0
                self.x = (xmin - half_x, xmax + half_x)
                self.y = (ymin - half_y, ymax + half_y)
        else:
            self.image = EMPTY_IMAGE

        self._latest_hash = current_hash

    def invalidate_cache(self):
        self.update(force=True)
