import bqplot
import numpy as np
import warnings
from astropy.visualization import AsinhStretch, LinearStretch, LogStretch, SqrtStretch

from glue.core.exceptions import IncompatibleAttribute
from glue.utils import color2hex, datetime64_to_mpl, ensure_numerical
from glue.viewers.common.layer_artist import LayerArtist
from glue.viewers.scatter.layer_artist import DensityMapLimits
from glue.viewers.scatter.state import ScatterLayerState
from glue_jupyter.bqplot.scatter.scatter_density_mark import GenericDensityMark

from ...utils import colormap_to_hexlist, float_or_none
from ..compatibility import ScatterGL, LinesGL

USE_GL = True

__all__ = ["BqplotScatterLayerArtist"]
EMPTY_IMAGE = np.zeros((10, 10, 4), dtype=np.uint8)


STRETCHES = {
    "linear": LinearStretch,
    "sqrt": SqrtStretch,
    "arcsinh": AsinhStretch,
    "log": LogStretch,
}

CMAP_PROPERTIES = {"cmap_mode", "cmap_att", "cmap_vmin", "cmap_vmax", "cmap"}
MARKER_PROPERTIES = {
    "size_mode",
    "size_att",
    "size_vmin",
    "size_vmax",
    "size_scaling",
    "size",
    "fill",
}
DENSITY_PROPERTIES = {"dpi", "stretch", "density_contrast"}
VISUAL_PROPERTIES = (
    CMAP_PROPERTIES
    | MARKER_PROPERTIES
    | DENSITY_PROPERTIES
    | {"color", "alpha", "zorder", "visible"}
)

LIMIT_PROPERTIES = {"x_min", "x_max", "y_min", "y_max"}
DATA_PROPERTIES = {
    "layer",
    "x_att",
    "y_att",
    "cmap_mode",
    "size_mode",
    "density_map",
    "vector_visible",
    "vx_att",
    "vy_att",
    "vector_arrowhead",
    "vector_mode",
    "vector_origin",
    "line_visible",
    "linestyle",
    "linewidth",
    "markers_visible",
    "vector_scaling",
    "vline_visible",
    "hline_visible",
}


def values_to_nan_separated_lines(values):
    """
    Construct x and y arrays for a single ``Lines`` mark that renders one line
    per value, using NaN values to separate the individual lines. The
    coordinate along the lines is 0 to 1, to be used with a [0:1] scale that
    is independent of the axes limits.
    """
    across = np.repeat(values.astype(np.float32), 3)
    across[2::3] = np.nan
    along = np.full(len(values) * 3, np.nan, dtype=np.float32)
    along[::3] = 0
    along[1::3] = 1
    return across, along


# Kept for backward compatibility with <= 0.17
class BqplotScatterLayerState(ScatterLayerState):
    def __init__(self, *args, **kwargs):
        warnings.warn("`BqplotScatterLayerState` is deprecated and will be removed in a "
                    "future version. Use `ScatterLayerState` instead", DeprecationWarning)
        super().__init__(*args, **kwargs)

class BqplotScatterLayerArtist(LayerArtist):

    _layer_state_cls = ScatterLayerState

    def __init__(self, view, viewer_state, layer_state=None, layer=None):

        super().__init__(
            viewer_state,
            layer_state=layer_state,
            layer=layer,
        )

        # Workaround for the fact that the solid line display choice is shown
        # as a dashed line.
        linestyle_display = {'solid': 'solid',
                             'dashed': '– – – – –',
                             'dotted': '· · · · · · · ·',
                             'dashdot': '– · – · – ·'}

        ScatterLayerState.linestyle.set_display_func(self.state, linestyle_display.get)

        # Watch for changes in the viewer state which would require the
        # layers to be redrawn
        self._viewer_state.add_global_callback(self._update_scatter)
        self.state.add_global_callback(self._update_scatter)

        self.state.add_callback("zorder", self._update_zorder)

        self.view = view

        # Scatter points

        self.scale_color_scatter = bqplot.ColorScale()
        self.scales_scatter = dict(
            self.view.scales,
            color=self.scale_color_scatter,
        )

        self.scatter_mark = ScatterGL(scales=self.scales_scatter, x=[0, 1], y=[0, 1])

        # Line

        lines_gl_cls = LinesGL
        self.line_mark_gl = lines_gl_cls(scales=self.view.scales, x=[0.], y=[0.])
        self.line_mark_gl.colors = [color2hex(self.state.color)]
        self.line_mark_gl.opacities = [self.state.alpha]
        self.line_mark_gl.visible = False

        # duplicate lines using base bqplot.Lines for linestyle default visible=False
        lines_cls = bqplot.Lines
        self.line_mark = lines_cls(scales=self.view.scales, x=[0.], y=[0.])
        self.line_mark.colors = [color2hex(self.state.color)]
        self.line_mark.opacities = [self.state.alpha]
        self.line_mark.visible = False

        # Vertical and horizontal lines, all rendered as a single Lines mark
        # each, with NaN values separating the individual lines. The scale for
        # the direction along the lines is an independent [0:1] scale so that
        # the lines always span the full height/width of the plot regardless
        # of the axes limits.

        self.scale_along_lines = bqplot.LinearScale(min=0, max=1)
        self.vline_mark = bqplot.Lines(scales=dict(self.view.scales,
                                                   y=self.scale_along_lines),
                                       x=[], y=[], visible=False)
        self.vline_mark.colors = [color2hex(self.state.color)]
        self.vline_mark.opacities = [self.state.alpha]
        self.hline_mark = bqplot.Lines(scales=dict(self.view.scales,
                                                   x=self.scale_along_lines),
                                       x=[], y=[], visible=False)
        self.hline_mark.colors = [color2hex(self.state.color)]
        self.hline_mark.opacities = [self.state.alpha]

        self._line_mode_auto_checked = False

        # Vectors

        self.scale_size_vector = bqplot.LinearScale(min=0, max=1)
        self.scale_color_vector = bqplot.ColorScale()
        self.scale_rotation_vector = bqplot.LinearScale(min=-np.pi, max=np.pi)
        self.scales_vector = dict(
            self.view.scales,
            size=self.scale_size_vector,
            color=self.scale_color_vector,
            rotation=self.scale_rotation_vector,
        )
        self.vector_mark = ScatterGL(
            scales=self.scales_vector,
            x=[0, 1],
            y=[0, 1],
            visible=False,
            marker="arrow",
        )

        vector_lines_cls = bqplot.Lines
        self.vector_lines = vector_lines_cls(scales=self.view.scales, x=[0.], y=[0.])
        self.vector_lines.colors = [color2hex(self.state.color)]
        self.vector_lines.visible = False

        # Density map

        self.density_auto_limits = DensityMapLimits()
        self.density_mark = GenericDensityMark(
            figure=self.view.figure,
            vmin=self.density_auto_limits.min,
            vmax=self.density_auto_limits.max,
            histogram2d_func=self.compute_density_map,
            visible=False
        )

        self.view.figure.marks = list(self.view.figure.marks) + [
            self.density_mark,
            self.scatter_mark,
            self.vline_mark,
            self.hline_mark,
            self.vector_mark,
            self.vector_lines,
        ]

    def _auto_enable_line_mode(self, x, y):
        # If, the first time the data are accessed, only one of the two
        # attributes can be resolved, the only meaningful way to show the layer
        # is as vertical or horizontal lines, so we enable the relevant mode.
        # This is done only once so that users can subsequently turn the lines
        # off without them coming back on every update.
        if self._line_mode_auto_checked:
            return
        self._line_mode_auto_checked = True
        if x is None and not self.state.hline_visible:
            self.state.hline_visible = True
        elif y is None and not self.state.vline_visible:
            self.state.vline_visible = True

    def compute_density_map(self, *args, **kwargs):
        try:
            density_map = self.state.compute_density_map(*args, **kwargs)
        except IncompatibleAttribute:
            self.disable_invalid_attributes(
                self._viewer_state.x_att,
                self._viewer_state.y_att,
            )
            return np.array([[np.nan]])
        else:
            self.enable()
        return density_map

    def _update_data(self):

        x = y = None

        if not self.state.density_map:

            try:
                x = ensure_numerical(self.layer[self._viewer_state.x_att].ravel())
                if x.dtype.kind == "M":
                    x = datetime64_to_mpl(x)
            except (IncompatibleAttribute, IndexError):
                pass

            try:
                y = ensure_numerical(self.layer[self._viewer_state.y_att].ravel())
                if y.dtype.kind == "M":
                    y = datetime64_to_mpl(y)
            except (IncompatibleAttribute, IndexError):
                pass

            # If only one of the two attributes can be resolved for the layer,
            # we can still show the values as vertical or horizontal lines, so
            # we only disable the layer if neither attribute can be resolved.
            if x is None and y is None:
                # The following includes a call to self.clear()
                self.disable_invalid_attributes(self._viewer_state.x_att,
                                                self._viewer_state.y_att)
                return
            else:
                self.enable()

            self._auto_enable_line_mode(x, y)

        if self.state.markers_visible and x is not None and y is not None:

            if self.state.density_map:
                self.scatter_mark.x = []
                self.scatter_mark.y = []
            else:
                self.scatter_mark.x = x.astype(np.float32).ravel()
                self.scatter_mark.y = y.astype(np.float32).ravel()

        else:
            self.scatter_mark.x = []
            self.scatter_mark.y = []

        if self.state.vline_visible and x is not None:
            self.vline_mark.x, self.vline_mark.y = values_to_nan_separated_lines(x)
        else:
            self.vline_mark.x = []
            self.vline_mark.y = []

        if self.state.hline_visible and y is not None:
            self.hline_mark.y, self.hline_mark.x = values_to_nan_separated_lines(y)
        else:
            self.hline_mark.x = []
            self.hline_mark.y = []

        if self.state.line_visible and x is not None and y is not None:
            self.line_mark_gl.x = x.astype(np.float32).ravel()
            self.line_mark_gl.y = y.astype(np.float32).ravel()
            self.line_mark.x = x.astype(np.float32).ravel()
            self.line_mark.y = y.astype(np.float32).ravel()
        else:
            self.line_mark_gl.x = [0.]
            self.line_mark_gl.y = [0.]
            self.line_mark.x = [0.]
            self.line_mark.y = [0.]

        if (
            self.state.vector_visible
            and self.state.vx_att is not None
            and self.state.vy_att is not None
            and x is not None
            and y is not None
        ):

            vx = ensure_numerical(self.layer[self.state.vx_att].ravel())
            vy = ensure_numerical(self.layer[self.state.vy_att].ravel())

            size = 50
            scale = self.state.vector_scaling

            length = np.sqrt(vx**2 + vy**2)
            angle = np.arctan2(vy, vx)

            self.scale_size_vector.min = np.nanmin(length)
            self.scale_size_vector.max = np.nanmax(length)

            self.vector_mark.x = x.astype(np.float32).ravel()
            self.vector_mark.y = y.astype(np.float32).ravel()
            self.vector_mark.default_size = int(size * scale * 4)
            self.vector_mark.size = length
            self.vector_mark.rotation = angle
            self.vector_mark.color = [color2hex(self.state.color)]

            vector_line_coords = self._build_line_vector_points(x, y, vx, vy)
            x_vector_coords = vector_line_coords[:, 0]
            y_vector_coords = vector_line_coords[:, 1]
            self.vector_lines.x = x_vector_coords
            self.vector_lines.y = y_vector_coords
        else:
            self.vector_mark.x = []
            self.vector_mark.y = []
            self.vector_lines.x = []
            self.vector_lines.y = []

    def _update_visual_attributes(self, changed, force=False):
        if not self.enabled:
            return

        if self.state.markers_visible:

            if self.state.density_map:

                if self.state.cmap_mode == "Fixed":
                    if force or "color" in changed or "cmap_mode" in changed:
                        self.density_mark.set_color(self.state.color)
                        self.density_mark.vmin = self.density_auto_limits.min
                        self.density_mark.vmax = self.density_auto_limits.max
                elif force or any(prop in changed for prop in CMAP_PROPERTIES):
                    self.density_mark.cmap = self.state.cmap
                    self.density_mark.vmin = self.state.cmap_vmin
                    self.density_mark.vmax = self.state.cmap_vmax

                if force or "stretch" in changed:
                    self.density_mark.stretch = self.state.stretch_object

                if force or "dpi" in changed:
                    self.density_mark.dpi = self._viewer_state.dpi

                if force or "density_contrast" in changed:
                    self.density_auto_limits.contrast = self.state.density_contrast
                    self.density_mark._update_rendered_image()

            else:

                if self.state.cmap_mode == "Fixed" or self.state.cmap_att is None:
                    if force or "color" in changed or "cmap_mode" in changed or "fill" in changed:
                        self.scatter_mark.color = None
                        self.scatter_mark.colors = [color2hex(self.state.color)]
                        self.scatter_mark.fill = self.state.fill
                elif force or any(prop in changed for prop in CMAP_PROPERTIES) or "fill" in changed:
                    self.scatter_mark.color = ensure_numerical(
                        self.layer[self.state.cmap_att].ravel(),
                    )
                    self.scatter_mark.fill = self.state.fill
                    self.scale_color_scatter.colors = colormap_to_hexlist(
                        self.state.cmap,
                    )
                    self.scale_color_scatter.min = float_or_none(self.state.cmap_vmin)
                    self.scale_color_scatter.max = float_or_none(self.state.cmap_vmax)

                if force or any(prop in changed for prop in MARKER_PROPERTIES):

                    if self.state.size_mode == "Fixed" or self.state.size_att is None:
                        self.scatter_mark.default_size = int(
                            self.state.size * self.state.size_scaling,
                        )
                        self.scatter_mark.size = None
                    else:
                        self.scatter_mark.default_size = int(self.state.size_scaling * 7)
                        s = ensure_numerical(self.layer[self.state.size_att].ravel())
                        s = ((s - self.state.size_vmin) /
                             (self.state.size_vmax - self.state.size_vmin))
                        np.clip(s, 0, 1, out=s)
                        s *= 0.95
                        s += 0.05
                        s *= self.scatter_mark.default_size
                        self.scatter_mark.size = s ** 2

        if self.state.line_visible:
            if force or "color" in changed:
                self.line_mark_gl.colors = [color2hex(self.state.color)]
                self.line_mark.colors = [color2hex(self.state.color)]
            if force or "linewidth" in changed:
                self.line_mark_gl.stroke_width = self.state.linewidth
                self.line_mark.stroke_width = self.state.linewidth

            if force or "linestyle" in changed:
                use_line_gl = True
                self.line_mark.colors = [color2hex(self.state.color)]
                if self.state.linestyle == "solid":
                    pass
                else:
                    use_line_gl = False
                    if self.state.linestyle == "dashdot":
                        self.line_mark.line_style = 'dash_dotted'
                    else:
                        self.line_mark.line_style = self.state.linestyle

                new_marks = []
                line_mark_added = False
                for mark in self.view.figure.marks:
                    if mark is self.line_mark_gl and not use_line_gl:
                        new_marks.append(self.line_mark)
                        line_mark_added = True
                    elif mark is self.line_mark and use_line_gl:
                        new_marks.append(self.line_mark_gl)
                        line_mark_added = True
                    else:
                        new_marks.append(mark)
                if not line_mark_added:
                    new_marks.append(self.line_mark_gl if use_line_gl else self.line_mark)

                self.view.figure.marks = new_marks

        for mark, lines_visible in ((self.vline_mark, self.state.vline_visible),
                                    (self.hline_mark, self.state.hline_visible)):

            if lines_visible:
                if force or "color" in changed:
                    mark.colors = [color2hex(self.state.color)]
                if force or "linewidth" in changed:
                    mark.stroke_width = self.state.linewidth
                if force or "linestyle" in changed:
                    if self.state.linestyle == "dashdot":
                        mark.line_style = "dash_dotted"
                    else:
                        mark.line_style = self.state.linestyle

        if (
            self.state.vector_visible
            and self.state.vx_att is not None
            and self.state.vy_att is not None
        ):
            self.vector_mark.visible = False
            self.vector_lines.visible = True

            if self.state.cmap_mode == "Fixed":
                if force or "color" in changed or "cmap_mode" in changed:
                    self.vector_mark.color = None
                    self.vector_mark.colors = [color2hex(self.state.color)]
                    self.vector_lines.colors = [color2hex(self.state.color)]
            elif force or any(prop in changed for prop in CMAP_PROPERTIES):
                self.vector_mark.color = ensure_numerical(
                    self.layer[self.state.cmap_att].ravel(),
                )
                self.scale_color_vector.colors = colormap_to_hexlist(self.state.cmap)
                self.scale_color_vector.min = float_or_none(self.state.cmap_vmin)
                self.scale_color_vector.max = float_or_none(self.state.cmap_vmax)

        for mark in [self.scatter_mark, self.line_mark_gl, self.line_mark,
                     self.vline_mark, self.hline_mark,
                     self.vector_mark, self.vector_lines, self.density_mark]:

            if mark is None:
                continue

            if force or "alpha" in changed:
                mark.opacities = [self.state.alpha]

        if force or "visible" in changed:
            self.scatter_mark.visible = self.state.visible and self.state.markers_visible
            self.line_mark.visible = self.state.visible and self.state.line_visible
            self.line_mark_gl.visible = self.state.visible and self.state.line_visible
            self.vline_mark.visible = self.state.visible and self.state.vline_visible
            self.hline_mark.visible = self.state.visible and self.state.hline_visible
            self.density_mark.visible = (self.state.visible and self.state.density_map
                                         and self.state.markers_visible)
            self.vector_lines.visible = self.state.visible and self.state.vector_visible

    def _update_scatter(self, force=False, **kwargs):

        if (
            self.density_mark is None
            or self.scatter_mark is None
            or self.line_mark_gl is None
            or self.line_mark is None
            or self.vline_mark is None
            or self.hline_mark is None
            or self.vector_mark is None
            or self.vector_lines is None
            or self._viewer_state.x_att is None
            or self._viewer_state.y_att is None
            or self.state.layer is None
        ):
            return

        # NOTE: we need to evaluate this even if force=True so that the cache
        # of updated properties is up to date after this method has been called.
        changed = self.pop_changed_properties()

        if force or len(changed & DATA_PROPERTIES) > 0:
            self._update_data()
            force = True

        if force or len(changed & VISUAL_PROPERTIES) > 0:
            self._update_visual_attributes(changed, force=force)

    def update(self):
        self._update_scatter(force=True)

    def remove(self):
        marks = self.view.figure.marks[:]
        marks.remove(self.density_mark)
        self.density_mark = None
        marks.remove(self.scatter_mark)
        self.scatter_mark = None
        if self.line_mark_gl in marks:
            marks.remove(self.line_mark_gl)
        self.line_mark_gl = None
        if self.line_mark in marks:
            marks.remove(self.line_mark)
        self.line_mark = None
        marks.remove(self.vline_mark)
        self.vline_mark = None
        marks.remove(self.hline_mark)
        self.hline_mark = None
        marks.remove(self.vector_mark)
        self.vector_mark = None
        marks.remove(self.vector_lines)
        self.vector_lines = None
        self.view.figure.marks = marks
        return super().remove()

    def clear(self):
        if self.scatter_mark is not None:
            self.scatter_mark.x = []
            self.scatter_mark.y = []
        if self.line_mark_gl is not None:
            self.line_mark_gl.x = [0.]
            self.line_mark_gl.y = [0.]
        if self.line_mark is not None:
            self.line_mark.x = [0.]
            self.line_mark.y = [0.]
        if self.vline_mark is not None:
            self.vline_mark.x = []
            self.vline_mark.y = []
        if self.hline_mark is not None:
            self.hline_mark.x = []
            self.hline_mark.y = []
        if self.vector_mark is not None:
            self.vector_mark.x = []
            self.vector_mark.y = []
        if self.vector_lines is not None:
            self.vector_lines.x = []
            self.vector_lines.y = []
        elif self.density_mark is not None:
            self.density_mark.image = EMPTY_IMAGE

    def _update_zorder(self, *args):
        sorted_layers = sorted(self.view.layers, key=lambda layer: layer.state.zorder)
        self.view.figure.marks = [
            item
            for layer in sorted_layers
            for item in (layer.density_mark,
                         layer.scatter_mark,
                         layer.line_mark_gl
                         if layer.state.linestyle == 'solid' else layer.line_mark,
                         layer.vline_mark,
                         layer.hline_mark,
                         layer.vector_mark,
                         layer.vector_lines)
            if item is not None
        ]

    def _build_line_vector_points(self, x, y, vx, vy):
        """
        Function builds an array of coordinate pairs separated by nans for plotting individual lines
        to replicate vector behaviour

        Returns: np.array
            array of structure ([x1, y1], [x2, y2], [np.nan, np.nan])
        """
        point_pairs = []
        for row in range(0, len(x)):
            length = np.sqrt(vx[row]**2 + vy[row]**2) * self.state.vector_scaling
            angle = np.arctan2(vy[row], vx[row])
            x_delta = length * np.cos(angle)
            y_delta = length * np.sin(angle)
            if self.state.vector_origin == 'tail':
                x1 = x[row]
                y1 = y[row]
                x2 = x[row] - x_delta
                y2 = y[row] - y_delta
            elif self.state.vector_origin == 'tip':
                x1 = x[row]
                y1 = y[row]
                x2 = x[row] + x_delta
                y2 = y[row] + y_delta
            elif self.state.vector_origin == 'middle':
                x1 = x[row] - x_delta / 2
                y1 = y[row] - y_delta / 2
                x2 = x[row] + x_delta / 2
                y2 = y[row] + y_delta / 2
            point_1 = [x1, y1]
            point_pairs.append(point_1)
            point_2 = [x2, y2]
            point_pairs.append(point_2)
            point_3 = [np.nan, np.nan]
            point_pairs.append(point_3)

        return np.array(point_pairs)
