import numpy as np

from glue_jupyter.bqplot.image.state import BqplotImageLayerState

from glue.viewers.image.layer_artist import BaseImageLayerArtist, ImageLayerArtist, ImageSubsetArray
from glue.viewers.image.state import ImageSubsetLayerState
from glue.core.fixed_resolution_buffer import ARRAY_CACHE, PIXEL_CACHE

from bqplot_image_gl import Contour

from .frb_mark import FRBImage

__all__ = ['BqplotImageLayerArtist', 'BqplotImageSubsetLayerArtist']


class BqplotImageLayerArtist(ImageLayerArtist):

    _layer_state_cls = BqplotImageLayerState

    def __init__(self, view, *args, **kwargs):
        super().__init__(view, *args, **kwargs)
        self.view = view
        self.contour_artist = Contour(image=self.view._composite_image.image,
                                      scales=self.view._composite_image.scales)
        self.view.figure.marks = list(self.view.figure.marks) + [self.contour_artist]

    def enable(self):
        if self.enabled:
            return

    def redraw(self):
        pass

    # The following four methods are a patch for an issue that is fixed
    # in glue-core with https://github.com/glue-viz/glue/pull/2099.
    # Once glue v0.16 is the minimum dependency of glue-jupyter we can
    # remove them.

    def remove(self):
        super().remove()
        self.uuid = None

    def _update_image(self, *args, **kwargs):
        if self.uuid is None:
            return
        super()._update_image(*args, **kwargs)

    def get_image_shape(self, *args, **kwargs):
        if self.uuid is None:
            return None
        else:
            return super().get_image_shape(*args, **kwargs)

    def get_image_data(self, *args, **kwargs):
        if self.uuid is None:
            return None
        else:
            return super().get_image_data(*args, **kwargs)

    def _update_visual_attributes(self, redraw=True):

        if not self.enabled:
            return

        super()._update_visual_attributes(redraw=redraw)

        self.contour_artist.visible = self.state.visible and self.state.contour_visible

        # TODO: change visual appearance of contour artist

    def _update_contour(self):
        # TODO: make it possible to customize number of contours
        # TODO: make it possible (maybe) to have different vmin/vmax for contour than for image
        self.contour_artist.image = self.image_artist.image
        self.contour_artist.level = np.linspace(self.state.v_min, self.state.v_max, 10)

    def _update_image(self, force=False, **kwargs):

        super()._update_image(force=force, **kwargs)

        # TODO: Determine under what conditions to update contours
        self._update_contour()


class BqplotImageSubsetLayerArtist(BaseImageLayerArtist):

    _layer_state_cls = ImageSubsetLayerState

    def __init__(self, view, viewer_state, layer_state=None, layer=None):

        super(BqplotImageSubsetLayerArtist, self).__init__(view, viewer_state,
                                                           layer_state=layer_state, layer=layer)

        # NOTE: we need to do this explicitly since BaseImageLayerArtist
        # actually stores this in self.axes rather than self.view.
        self.view = view

        self.subset_array = ImageSubsetArray(self._viewer_state, self)

        self.image_artist = FRBImage(view, self.subset_array)
        self.view.figure.marks = list(self.view.figure.marks) + [self.image_artist, self.contour_artist]

    def _update_data(self):
        self.image_artist.invalidate_cache()

    def _update_visual_attributes(self, redraw=True):

        if not self.enabled:
            return

        self.image_artist.visible = self.state.visible
        self.image_artist.opacity = self.state.alpha

    def _update_image(self, force=False, **kwargs):

        if self.subset_array is None or self.state.layer is None:
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
        self.subset_array = None
        marks = self.view.figure.marks[:]
        marks.remove(self.image_artist)
        self.image_artist = None
        self.view.figure.marks = marks

    def enable(self, redraw=True):
        if self.enabled:
            return
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
