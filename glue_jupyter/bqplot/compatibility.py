from bqplot_image_gl import ImageGL
import bqplot

ScatterGL = None
if hasattr(bqplot, "ScatterGL"):
    ScatterGL = bqplot.ScatterGL
else:
    import bqplot_gl

    ScatterGL = bqplot_gl.marks.ScatterGL

# Note: bqplot-gl (used as the GL backend with bqplot 0.13) ships a LinesGL
# whose frontend does not render the line at all, so we always use the
# implementation from bqplot-image-gl, which renders correctly with both
# bqplot 0.12 and 0.13.
from bqplot_image_gl import LinesGL

__all__ = ["ScatterGL", "ImageGL", "LinesGL"]
