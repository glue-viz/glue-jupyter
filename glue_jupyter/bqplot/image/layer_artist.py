import skimage.measure

from glue_jupyter.bqplot.image.state import BqplotImageLayerState
from glue.viewers.image.layer_artist import BaseImageLayerArtist, ImageLayerArtist, ImageSubsetArray
from glue.viewers.image.state import ImageSubsetLayerState
from glue.core.fixed_resolution_buffer import ARRAY_CACHE, PIXEL_CACHE
from glue.core.units import UnitConverter
from ...link import link

from bqplot_image_gl import Contour

from .frb_mark import FRBImage

__all__ = ['BqplotImageLayerArtist', 'BqplotImageSubsetLayerArtist']


class BqplotImageLayerArtist(ImageLayerArtist):

    _layer_state_cls = BqplotImageLayerState

    def __init__(self, view, *args, **kwargs):
        super().__init__(view, *args, **kwargs)
        # TODO: we should probably use a lru cache to avoid having a 'memleak'
        self._contour_line_cache = {}
        self.view = view
        self.contour_artist = Contour(contour_lines=[], label_steps=1000,
                                      scales=self.view._composite_image.scales,
                                      color=self.state.contour_colors,
                                      visible=self.state.visible and self.state.contour_visible)
        self.view.figure.marks = list(self.view.figure.marks) + [self.contour_artist]
        link((self.state, 'contour_colors'), (self.contour_artist, 'color'))
        link((self.state, 'levels'), (self.contour_artist, 'level'))
        link((self.state, 'labels'), (self.contour_artist, 'label'))

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
        marks = list(self.view.figure.marks)
        if self.contour_artist in marks:
            marks.remove(self.contour_artist)
        self.view.figure.marks = marks
        self.uuid = None

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

    def _update_visual_attributes(self):

        super()._update_visual_attributes()

        if self.state.visible and not self.state.bitmap_visible:
            self.composite.set(self.uuid, visible=False)
            self.composite_image.invalidate_cache()

        was_visible = self.contour_artist.visible
        self.contour_artist.visible = self.state.visible and self.state.contour_visible
        if not was_visible and self.contour_artist.visible:
            # switching from invisible to visible may leave the contour lines in an inconsistent
            # state, since we don't update them when invisible, so we have to update them
            self._update_contour_lines()

        self.redraw()

    def _update_contour_lines(self):
        if not self.contour_artist.visible:
            return  # don't compute if not visible
        contour_data = self.get_image_data()
        if contour_data is None:
            self.contour_artist.contour_lines = []
            return

        # As the levels may be specified in a different unit we should convert
        # the data to match the units of the levels (we do it this way around
        # so that the labels are shown in the new units)

        converter = UnitConverter()

        contour_data = converter.to_unit(self.state.layer,
                                         self.state.attribute,
                                         contour_data,
                                         self.state.attribute_display_unit)

        for level in self.state.levels:
            if level not in self._contour_line_cache:
                contour_line_set = skimage.measure.find_contours(contour_data.T, level)
                contour_line_set = [k for k in contour_line_set]
                self._contour_line_cache[level] = contour_line_set
        self.contour_artist.level = self.state.levels
        self.contour_artist.contour_lines = [self._contour_line_cache[level] for level
                                             in self.state.levels]

    def _update_image(self, force=False, **kwargs):
        # ideally, we call super first, and see if we have any extra work to do
        # but because .pop_changed_properties  pops all changes, we don't have access to it
        # super()._update_image(force=force, **kwargs)
        if self.uuid is None or self.state.attribute is None or self.state.layer is None:
            return

        # NOTE: we need to evaluate this even if force=True so that the cache
        # of updated properties is up to date after this method has been called.
        changed = self.pop_changed_properties()

        if force or any(prop in changed for prop in ('layer', 'attribute',
                                                     'slices', 'x_att', 'y_att')):
            self._update_image_data()
            force = True  # make sure scaling and visual attributes are updated

        if force or any(prop in changed for prop in ('v_min', 'v_max', 'contrast',
                                                     'bias', 'alpha', 'color_mode',
                                                     'cmap', 'color', 'zorder',
                                                     'visible', 'stretch', 'stretch_parameters',
                                                     'bitmap_visible', 'contour_visible')):
            self._update_visual_attributes()
        if force or 'levels' in changed:
            self._update_contour_lines()

    def _update_image_data(self, *args, **kwargs):
        self.composite_image.invalidate_cache()
        # if the image data change, the contour lines are invalid
        self._contour_line_cache.clear()
        self._update_contour_lines()


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
        self.view.figure.marks = list(self.view.figure.marks) + [self.image_artist]

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

        # NOTE: we need to evaluate this even if force=True so that the cache
        # of updated properties is up to date after this method has been called.
        changed = self.pop_changed_properties()

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
        if hasattr(self, 'image_artist') and self.image_artist is not None:
            self.image_artist.invalidate_cache()
            self._update_visual_attributes(redraw=redraw)

    def update(self, *event):
        ARRAY_CACHE.pop(self.state.uuid, None)
        PIXEL_CACHE.pop(self.state.uuid, None)
        self._update_image(force=True)
        self.redraw()

    def redraw(self):
        pass
