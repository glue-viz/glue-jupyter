# NOTE: The following MultiSliceHelper is adapted from the Qt version and there
# is enough overlap that we could consider having a base class for the two.

from ipywidgets import IntSlider

from glue.viewers.image.state import AggregateSlice
from glue.utils.decorators import avoid_circular

__all__ = ['MultiSliceWidgetHelper']


class MultiSliceWidgetHelper(object):

    def __init__(self, viewer_state=None, layout=None):

        self.viewer_state = viewer_state

        self.layout = layout

        self.viewer_state.add_callback('x_att', self.sync_sliders_from_state)
        self.viewer_state.add_callback('y_att', self.sync_sliders_from_state)
        self.viewer_state.add_callback('slices', self.sync_sliders_from_state)
        self.viewer_state.add_callback('reference_data', self.sync_sliders_from_state)

        self._sliders = []

        self._reference_data = None
        self._x_att = None
        self._y_att = None

        self.sync_sliders_from_state()

    @property
    def data(self):
        return self.viewer_state.reference_data

    def _clear(self):
        self.layout.children = []
        self._sliders = []

    @avoid_circular
    def sync_state_from_sliders(self, *args):
        slices = []
        for i, slider in enumerate(self._sliders):
            if slider is not None:
                slices.append(slider.value)
            else:
                slices.append(self.viewer_state.slices[i])
        self.viewer_state.slices = tuple(slices)

    @avoid_circular
    def sync_sliders_from_state(self, *args):

        if self.data is None or self.viewer_state.x_att is None or self.viewer_state.y_att is None:
            return

        if self.viewer_state.x_att is self.viewer_state.y_att:
            return

        # Update sliders if needed

        if (self.viewer_state.reference_data is not self._reference_data or
                self.viewer_state.x_att is not self._x_att or
                self.viewer_state.y_att is not self._y_att):

            self._reference_data = self.viewer_state.reference_data
            self._x_att = self.viewer_state.x_att
            self._y_att = self.viewer_state.y_att

            self._clear()

            for i in range(self.data.ndim):

                if i == self.viewer_state.x_att.axis or i == self.viewer_state.y_att.axis:
                    self._sliders.append(None)
                    continue

                if self.viewer_state.reference_data.coords is None:
                    label = self.viewer_state.reference_data.pixel_component_ids[i].label
                else:
                    label = self.viewer_state.reference_data.world_component_ids[i].label
                slider = IntSlider(min=0, max=self.data.shape[i]-1, description=label)

                slider.observe(self.sync_state_from_sliders, 'value')
                self._sliders.append(slider)
                self.layout.children += (slider,)

        for i in range(self.data.ndim):
            if self._sliders[i] is not None:
                if isinstance(self.viewer_state.slices[i], AggregateSlice):
                    self._sliders[i].value = self.viewer_state.slices[i].center
                else:
                    self._sliders[i].value = self.viewer_state.slices[i]
