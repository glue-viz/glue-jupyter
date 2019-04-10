import numpy as np
import matplotlib.cm

from glue.viewers.image.layer_artist import BaseImageLayerArtist, ImageLayerArtist, ImageSubsetArray
from glue.viewers.image.state import ImageSubsetLayerState
from glue.core.fixed_resolution_buffer import ARRAY_CACHE, PIXEL_CACHE

from .frb_mark import FRBImage


class BqplotImageLayerArtist(ImageLayerArtist):

    def redraw(self):
        pass


class BqplotImageSubsetLayerArtist(BaseImageLayerArtist):

    _layer_state_cls = ImageSubsetLayerState

    def __init__(self, axes, viewer_state, layer_state=None, layer=None):

        super(BqplotImageSubsetLayerArtist, self).__init__(axes, viewer_state,
                                                           layer_state=layer_state, layer=layer)

        self.subset_array = ImageSubsetArray(self._viewer_state, self)

        self.image_artist = FRBImage(axes, self.subset_array)
        self.axes.figure.marks = list(self.axes.figure.marks) + [self.image_artist]

    def _update_data(self):
        self.image_artist.invalidate_cache()

    def _update_visual_attributes(self, redraw=True):

        if not self.enabled:
            return

        self.image_artist.visible  = self.state.visible
        self.image_artist.opacity = self.state.alpha

    def _update_image(self, force=False, **kwargs):

        if self.state.layer is None:
            return

        changed = set() if force else self.pop_changed_properties()

        if force or any(prop in changed for prop in ('layer', 'attribute', 'color',
                                                     'x_att', 'y_att', 'slices')):
            self._update_data()
            force = True  # make sure scaling and visual attributes are updated

        if force or any(prop in changed for prop in ('zorder', 'visible', 'alpha')):
            self._update_visual_attributes()

    def remove(self):
        super(BqplotImageSubsetLayerArtist, self).remove()
        self.image_artist.invalidate_cache()
        ARRAY_CACHE.pop(self.state.uuid, None)
        PIXEL_CACHE.pop(self.state.uuid, None)

    def enable(self, redraw=True):
        super(BqplotImageSubsetLayerArtist, self).enable()
        # We need to now ensure that image_artist, which may have been marked
        # as not being visible when the layer was cleared is made visible
        # again.
        if hasattr(self, 'image_artist'):
            self.image_artist.invalidate_cache()
            self._update_visual_attributes(redraw=redraw)

    def update(self, *event):
        ARRAY_CACHE.pop(self.state.uuid, None)
        PIXEL_CACHE.pop(self.state.uuid, None)
        self._update_image(force=True)
        self.redraw()

    def redraw(self):
        pass
