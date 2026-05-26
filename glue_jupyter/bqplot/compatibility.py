# We deliberately take LinesGL from bqplot-image-gl rather than bqplot-gl:
# bqplot-gl (the GL backend used with bqplot 0.13) ships a LinesGL whose
# frontend does not render the line at all, whereas the bqplot-image-gl
# implementation renders correctly with both bqplot 0.12 and 0.13.
from bqplot_image_gl import ImageGL, LinesGL
import bqplot

ScatterGL = None
if hasattr(bqplot, "ScatterGL"):
    ScatterGL = bqplot.ScatterGL
else:
    import bqplot_gl

    ScatterGL = bqplot_gl.marks.ScatterGL

__all__ = ["ScatterGL", "ImageGL", "LinesGL"]
