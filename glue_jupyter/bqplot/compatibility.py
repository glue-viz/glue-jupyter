from bqplot_image_gl import ImageGL
import bqplot

ScatterGL = None
if hasattr(bqplot, "ScatterGL"):
    ScatterGL = bqplot.ScatterGL
else:
    import bqplot_gl

    ScatterGL = bqplot_gl.marks.ScatterGL


__all__ = ["ScatterGL", "ImageGL"]
