import math
import numpy as np

from bqplot import ColorScale
from bqplot_image_gl import ImageGL
from bqplot_image_gl.viewlistener import ViewListener

from traitlets import Float, Instance, Any

from matplotlib.colors import Colormap

from mpl_scatter_density.fixed_data_density_helper import FixedDataDensityHelper
from mpl_scatter_density.color import make_cmap

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
        The bqplot figure the density plot will be added to
    histogram2d_func : callable
        The function (or callable instance) to use for computing the 2D
        histogram - this should take the arguments ``bins`` and ``range`` as
        defined by :func:`~numpy.histogram2d`.
    dpi : int or `None`
        The number of dots per inch to include in the density map.
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


    cmap = Instance(Colormap, allow_none=True)
    alpha = Float(default_value=1.)
    vmin = Any(allow_none=True)
    vmax = Any(allow_none=True)

    dpi = Float(default_value=100.)
    external_padding = Float(default_value=0.1)

    def __init__(self, *, figure, histogram2d_func, cmap=None, color=None, alpha=None, vmin=None, vmax=None, dpi=None, external_padding=None):

        # FIXME: need to use weakref to avoid circular references

        self._figure = figure
        self._histogram2d_func = histogram2d_func

        self._counts = None

        if color is not None:
            self.set_color(color)
        elif cmap is not None:
            self.cmap = cmap
        else:
            self.set_color('black')

        if alpha is not None:
            self.alpha = alpha

        self.vmin = vmin
        self.vmax = vmax

        if dpi is not None:
            self.dpi = dpi

        if external_padding is not None:
            self.external_padding = external_padding

        self.observe(self._debounced_update_counts, 'dpi')
        self.observe(self._debounced_update_counts, 'external_padding')

        self.observe(self._update_rendered_image, 'cmap')
        self.observe(self._update_rendered_image, 'alpha')
        self.observe(self._update_rendered_image, 'vmin')
        self.observe(self._update_rendered_image, 'vmax')

        self._scale_image = ColorScale()
        self._scales = {'x': self._figure.axes[0].scale,
                       'y': self._figure.axes[1].scale,
                       'image': self._scale_image}

        super().__init__(image=EMPTY_IMAGE, scales=self._scales)

        self._figure.axes[0].scale.observe(self._debounced_update_counts, 'min')
        self._figure.axes[0].scale.observe(self._debounced_update_counts, 'max')
        self._figure.axes[1].scale.observe(self._debounced_update_counts, 'min')
        self._figure.axes[1].scale.observe(self._debounced_update_counts, 'max')

        self._shape = None
        self._setup_view_listener()

    def _setup_view_listener(self):
        self._vl = ViewListener(widget=self._figure,
                                css_selector=".plotarea_events")
        self._vl.observe(self._on_view_change, names=['view_data'])

    def _on_view_change(self, *args):
        views = sorted(self._vl.view_data)
        if len(views) > 0:
            first_view = self._vl.view_data[views[0]]
            self._shape = (int(first_view['height']), int(first_view['width']))
        else:
            self._shape = None
        self._debounced_update_counts()

    @debounced(method=True, delay_seconds=0.1)
    def _debounced_update_counts(self, *args, **kwargs):
        return self._update_counts(self, *args, **kwargs)

    def _update_counts(self, *args, **kwargs):

        # Shape can be (0, 0) when viewer was created and then destroyed.
        if self._shape is None or np.allclose(self._shape, 0):
            return

        # Get current limits from the plot
        xmin = self._figure.axes[0].scale.min
        xmax = self._figure.axes[0].scale.max
        ymin = self._figure.axes[1].scale.min
        ymax = self._figure.axes[1].scale.max

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

        # Apply DPI
        if self.dpi is not None:
            nx = max(1, int(nx * self.dpi / 100))
            ny = max(1, int(ny * self.dpi / 100))

        # Get the array and assign it to the artist
        image = self._histogram2d_func(bins=(ny, nx), range=[(ymin, ymax), (xmin, xmax)])

        with self.hold_sync():
            if image is not None:
                self._counts = image
                self.x = (xmin, xmax)
                self.y = (ymin, ymax)
            else:
                self._counts = None
            self._update_rendered_image()

    def _update_rendered_image(self, *args, **kwargs):

        if self._counts is None:
            self.image = EMPTY_IMAGE
            return

        vmin = self.vmin or np.nanmin
        vmax = self.vmax or np.nanmax

        if callable(vmin):
            vmin = vmin(self._counts)

        if callable(vmax):
            vmax = vmax(self._counts)

        normalized_counts = (self._counts - vmin) / (vmax - vmin)

        colormapped_counts = self.cmap(normalized_counts)

        if self.alpha is not None:
            colormapped_counts[:, :, 3] *= self.alpha

        self.image = colormapped_counts

    def set_color(self, color):
        if color is not None:
            self.cmap = make_cmap(color)


class ScatterDensityMark(GenericDensityMark):
    """
    Bqplot artist to make a density plot of (x, y) scatter data.

    Parameters
    ----------
    figure : bqplot.figure
        The bqplot figure the density plot will be added to
    x, y : iterable
        The data to plot.
    c : iterable
        Values to use for color-encoding. This is meant to be the same as
        the argument with the same name in :meth:`~matplotlib.axes.Axes.scatter`
        although for now only 1D iterables of values are accepted. Note that
        values are averaged inside each pixel of the density map *before*
        applying the colormap, which in some cases will be different from what
        the average color of markers would have been inside each pixel.
    dpi : int or `None`
        The number of dots per inch to include in the density map.
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
    dpi : int or `None`
        The number of dots per inch to include in the density map. To use
        the native resolution of the drawing device, set this to None.
    """

    def __init__(self, figure, x, y, c=None, **kwargs):
        self.histogram2d_helper = FixedDataDensityHelper(figure, x, y, c=c)
        super().__init__(figure=figure, histogram2d_func=self.histogram2d_helper,
                         **kwargs)

    def set_xy(self, x, y):
        self.histogram2d_helper.set_xy(x, y)

    def set_c(self, c):
        self.histogram2d_helper.set_c(c)
