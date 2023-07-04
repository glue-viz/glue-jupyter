import math
import numpy as np

from bqplot import ColorScale
from bqplot_image_gl import ImageGL
from bqplot_image_gl.viewlistener import ViewListener

from ...utils import debounced

__all__ = ['GenericDensityMark']

EMPTY_IMAGE = np.zeros((10, 10, 4), dtype=np.uint8)

# TODO: support norm?


class GenericDensityMark(ImageGL):
    """
    Bqplot mark to make a density plot given a helper histogram function.

    This is a more generic form of ``ScatterDensityMark``. Here, we can
    initialize the class with a histogram function that just takes bins and the
    range of values, and returns a density array. This is useful for cases
    where the data might be changing dynamically over time.

    Parameters
    ----------
    figure : bqplot.figure
        The figure
    histogram2d_func : callable
        The function (or callable instance) to use for computing the 2D
        histogram - this should take the arguments ``bins`` and ``range`` as
        defined by :func:`~numpy.histogram2d` as well as a ``pressed`` keyword
        argument that indicates whether the user is currently panning/zooming.
    dpi : int or `None`
        The number of dots per inch to include in the density map. To use
        the native resolution of the figure, use `None`.
    cmap : `matplotlib.colors.Colormap`
        The colormap to use for the density map.
    color : str or tuple
        The color to use for the density map. This can be any valid
        Matplotlib color. If specified, this takes precedence over the
        colormap.
    alpha : float
        Overall transparency of the density map.
    vmin, vmax : float or func
        The lower and upper levels used for scaling the density map. These can
        optionally be functions that take the density array and returns a single
        value (e.g. a function that returns the 5% percentile, or the minimum).
        This is useful since when zooming in/out, the optimal limits change.
    """
    def __init__(self, *, figure, histogram2d_func, dpi=None, cmap=None, color=None, alpha=None, vmin=None, vmax=None):

        # FIXME: need to use weakref to avoid circular references
        self.figure = figure

        self._external_padding = 0

        self.scale_image = ColorScale()
        self.scales = {'x': self.figure.axes[0].scale,
                       'y': self.figure.axes[1].scale,
                       'image': self.scale_image}

        super().__init__(image=EMPTY_IMAGE, scales=self.scales)

        self.histogram2d_func = histogram2d_func

        self.figure.axes[0].scale.observe(self.debounced_update, 'min')
        self.figure.axes[0].scale.observe(self.debounced_update, 'max')
        self.figure.axes[1].scale.observe(self.debounced_update, 'min')
        self.figure.axes[1].scale.observe(self.debounced_update, 'max')

        self._shape = None
        self._setup_view_listener()

        # NOTE: we deliberately don't call .update() here because when FRBImage
        # is created for the main composite image layer the composite arrays
        # haven't been set up yet, and for subset layers the layer gets force
        # updated anyway when the layers are added to the viewer.

    def _setup_view_listener(self):
        self._vl = ViewListener(widget=self.figure,
                                css_selector=".plotarea_events")
        self._vl.observe(self._on_view_change, names=['view_data'])

    def _on_view_change(self, *args):
        views = sorted(self._vl.view_data)
        if len(views) > 0:
            first_view = self._vl.view_data[views[0]]
            self._shape = (int(first_view['height']), int(first_view['width']))
        else:
            self._shape = None
        self.debounced_update()

    @debounced(method=True, delay_seconds=0.1)
    def debounced_update(self, *args, **kwargs):
        return self.update(self, *args, **kwargs)

    @property
    def external_padding(self):
        return self._external_padding

    @external_padding.setter
    def external_padding(self, value):
        previous_value = self._external_padding
        self._external_padding = value
        if value > previous_value:  # no point updating if the value is smaller than before
            self.debounced_update()

    def update(self, *args, **kwargs):

        # Shape can be (0, 0) when viewer was created and then destroyed.
        if self._shape is None or np.allclose(self._shape, 0):
            return

        # Get current limits from the plot
        xmin = self.figure.axes[0].scale.min
        xmax = self.figure.axes[0].scale.max
        ymin = self.figure.axes[1].scale.min
        ymax = self.figure.axes[1].scale.max

        if xmin is None or xmax is None or ymin is None or ymax is None:
            return

        ny, nx = self._shape

        # Expand beyond the boundary
        if self.external_padding != 0:
            dx = (xmax - xmin)
            dy = (ymax - ymin)
            xmin, xmax = xmin - dx * self.external_padding, xmax + dx * self.external_padding
            ymin, ymax = ymin - dy * self.external_padding, ymax + dy * self.external_padding
            nx *= math.ceil(1 + 2 * self.external_padding)
            ny *= math.ceil(1 + 2 * self.external_padding)

        # Get the array and assign it to the artist
        image = self.histogram2d_func(bins=(ny, nx), range=[(ymin, ymax), (xmin, xmax)])

        if image is not None:
            with self.hold_sync():
                import matplotlib.pyplot as plt
                self.image = plt.cm.viridis(image.astype(np.float32))
                self.x = (xmin, xmax)
                self.y = (ymin, ymax)
        else:
            self.image = EMPTY_IMAGE

    def invalidate_cache(self):
        self.update()
