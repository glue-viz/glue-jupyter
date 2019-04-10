import numpy as np
import matplotlib.cm

from glue.viewers.image.layer_artist import ImageLayerArtist


def _mask_to_rgba_data(mask, color):
    r, g, b = matplotlib.colors.to_rgb(color)
    rgba = np.zeros(mask.shape + (4,), dtype=np.uint8)
    rgba[mask.astype(np.bool),3] = 0.5 * 255
    rgba[...,0:3] = r * 255, g * 255, b * 255
    rgba[mask,3] = 255
    rgba[~mask,3] = 0
    return rgba


class BqplotImageLayerArtist(ImageLayerArtist):

    def redraw(self):
        pass
