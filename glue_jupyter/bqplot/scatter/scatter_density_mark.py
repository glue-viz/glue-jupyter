import math
import numpy as np

from bqplot import ColorScale
from bqplot_image_gl import ImageGL
from bqplot_image_gl.viewlistener import ViewListener

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

        self._counts = None

        self._dpi = dpi

        if color is not None:
            self.set_color(color)
        elif cmap is not None:
            self.set_cmap(cmap)
        else:
            self.set_color('black')

        self._alpha = alpha

        if vmin is not None or vmax is not None:
            self.set_clim(vmin, vmax)
        else:
            self.set_clim(np.nanmin, np.nanmax)

        # FIXME: need to use weakref to avoid circular references
        self.figure = figure

        self._external_padding = 0.1

        self.scale_image = ColorScale()
        self.scales = {'x': self.figure.axes[0].scale,
                       'y': self.figure.axes[1].scale,
                       'image': self.scale_image}

        super().__init__(image=EMPTY_IMAGE, scales=self.scales)

        self.histogram2d_func = histogram2d_func

        self.figure.axes[0].scale.observe(self.debounced_update_counts, 'min')
        self.figure.axes[0].scale.observe(self.debounced_update_counts, 'max')
        self.figure.axes[1].scale.observe(self.debounced_update_counts, 'min')
        self.figure.axes[1].scale.observe(self.debounced_update_counts, 'max')

        self._shape = None
        self._setup_view_listener()

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
        self.debounced_update_counts()

    @debounced(method=True, delay_seconds=0.1)
    def debounced_update_counts(self, *args, **kwargs):
        return self.update_counts(self, *args, **kwargs)

    @property
    def external_padding(self):
        return self._external_padding

    @external_padding.setter
    def external_padding(self, value):
        previous_value = self._external_padding
        self._external_padding = value
        if value > previous_value:  # no point updating if the value is smaller than before
            self.debounced_update()

    def update_counts(self, *args, **kwargs):

        # Shape can be (0, 0) when viewer was created and then destroyed.
        if self._shape is None or np.allclose(self._shape, 0):
            return

        # Get current limits from the plot
        xmin = self.figure.axes[0].scale.min
        xmax = self.figure.axes[0].scale.max
        ymin = self.figure.axes[1].scale.min
        ymax = self.figure.axes[1].scale.max

        print(xmin, xmax, ymin, ymax)

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
        if self._dpi is not None:
            nx = int(nx * self._dpi / 100)
            ny = int(ny * self._dpi / 100)

        # Get the array and assign it to the artist
        image = self.histogram2d_func(bins=(ny, nx), range=[(ymin, ymax), (xmin, xmax)])

        with self.hold_sync():
            if image is not None:
                self._counts = image
                self.x = (xmin, xmax)
                self.y = (ymin, ymax)
            else:
                self._counts = None
            self._update_rendered_image()

    def _update_rendered_image(self):

        if self._counts is None:
            self.image = EMPTY_IMAGE
            return

        if callable(self._density_vmin):
            vmin = self._density_vmin(self._counts)
        else:
            vmin = self._density_vmin

        if callable(self._density_vmax):
            vmax = self._density_vmax(self._counts)
        else:
            vmax = self._density_vmax

        normalized_counts = (self._counts - vmin) / (vmax - vmin)

        colormapped_counts = self._cmap(normalized_counts)

        if self._alpha is not None:
            colormapped_counts[:, :, 3] *= self._alpha

        self.image = colormapped_counts

    def invalidate_cache(self):
        self.update()

    def set_color(self, color):
        if color is not None:
            self.set_cmap(make_cmap(color))

    def set_cmap(self, cmap):
        self._cmap = cmap
        self._update_rendered_image()

    def set_clim(self, vmin, vmax):
        self._density_vmin = vmin
        self._density_vmax = vmax
        self._update_rendered_image()

    def set_norm(self, norm):
        raise NotImplementedError()


class ScatterDensityMark(GenericDensityMark):
    """
    Bqplot artist to make a density plot of (x, y) scatter data.

    Parameters
    ----------
    figure : bqplot.figure
        The figure
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
        The number of dots per inch to include in the density map. To use
        the native resolution of the drawing device, set this to None.
    downres_factor : int
        For interactive devices, when panning, the density map will
        automatically be made at a lower resolution and including only a
        subset of the points. The new dpi of the figure when panning will
        then be dpi / downres_factor, and the number of elements in the
        arrays will be reduced by downres_factor**2.
    cmap : `matplotlib.colors.Colormap`
        The colormap to use for the density map.
    color : str or tuple
        The color to use for the density map. This can be any valid
        Matplotlib color. If specified, this takes precedence over the
        colormap.
    alpha : float
        Overall transparency of the density map.
    norm : `matplotlib.colors.Normalize`
        The normalization class for the density map.
    vmin, vmax : float or func
        The lower and upper levels used for scaling the density map. These can
        optionally be functions that take the density array and returns a single
        value (e.g. a function that returns the 5% percentile, or the minimum).
        This is useful since when zooming in/out, the optimal limits change.
    update_while_panning : bool, optional
        Whether to compute histograms on-the-fly while panning.
    kwargs
        Any additional keyword arguments are passed to AxesImage.
    """

    def __init__(self, figure, x, y, downres_factor=4, c=None, **kwargs):
        self.histogram2d_helper = FixedDataDensityHelper(figure, x, y, c=c,
                                                         downres_factor=downres_factor)
        super().__init__(figure=figure, histogram2d_func=self.histogram2d_helper,
                         **kwargs)

    def set_xy(self, x, y):
        self.histogram2d_helper.set_xy(x, y)

    def set_c(self, c):
        self.histogram2d_helper.set_c(c)

    # def on_press(self, event=None, force=False):
    #     if not force:
    #         if self._update_while_panning and self.histogram2d_helper._downres_factor == 1:
    #             return
    #     self.histogram2d_helper.downres()
    #     return super().on_press(force=force)

    # def on_release(self, event=None):
    #     self.histogra).on_release()
