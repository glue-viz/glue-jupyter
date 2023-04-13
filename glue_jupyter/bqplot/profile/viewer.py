import numpy as np

from glue.core.units import UnitConverter
from glue.core.subset import roi_to_subset_state
from glue.core.roi import RangeROI
from glue.viewers.profile.state import ProfileViewerState

from ..common.viewer import BqplotBaseView

from .layer_artist import BqplotProfileLayerArtist

from astropy import units as u
from astropy.visualization.wcsaxes.formatter_locator import ScalarFormatterLocator
from astropy.wcs.wcsapi import SlicedLowLevelWCS

from glue.core.component_id import PixelComponentID
from glue_jupyter.common.state_widgets.layer_profile import ProfileLayerStateWidget
from glue_jupyter.common.state_widgets.viewer_profile import ProfileViewerStateWidget

__all__ = ['BqplotProfileView']


class BqplotProfileView(BqplotBaseView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    is2d = False

    _state_cls = ProfileViewerState
    _options_cls = ProfileViewerStateWidget
    _data_artist_cls = BqplotProfileLayerArtist
    _subset_artist_cls = BqplotProfileLayerArtist
    _layer_style_widget_cls = ProfileLayerStateWidget

    tools = ['bqplot:home', 'bqplot:panzoom', 'bqplot:panzoom_x', 'bqplot:panzoom_y',
             'bqplot:xrange']

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.state.add_callback('x_att', self._update_axes)
        self.state.add_callback('normalize', self._update_axes)
        self.state.add_callback('x_display_unit', self._update_axes)
        self.state.add_callback('y_display_unit', self._update_axes)
        self._update_axes()

        self.formatter_locator = ScalarFormatterLocator(number=5, unit=u.one, format='%.3g')
        self.scale_x.observe(self._update_labels, names=['min', 'max'])
        self.scale_y.observe(self._update_labels, names=['min', 'max'])
        self.state.add_callback('x_display_unit', self._update_labels)
        self.state.add_callback('x_show_world', self._update_labels)
        self.state.add_callback('x_display_unit', self._update_labels)

    def _update_labels(self, *args):

        if not isinstance(self.state.x_att, PixelComponentID) or not self.state.x_show_world:
            self.axis_x.tick_values = None
            self.axis_x.tick_labels = None
            return

        # Get WCS to use to convert pixel coordinates to world coordinates
        # TODO: slice WCS with >1 dimensions
        coords = self.state.reference_data.coords

        if coords.pixel_n_dim > 1:
            # As in ProfileLayerState.update_profile, we slice out other dimensions
            # TODO: if axes are correlated we should warn the user somehow
            # that the values are only true for a certain slice
            slices = tuple(slice(None) if idx == self.state.x_att.axis else 0 for idx in range(coords.pixel_n_dim))
            wcs_sub = SlicedLowLevelWCS(coords, slices)
        else:
            wcs_sub = self.state.reference_data.coords

        # TODO: make sure we deal correctly with units when non-standard unit is given

        # As we can't trust that the lower and upper values will be defined,
        # we need to sample the axis at a number of points to determine the
        # lower and upper values to use
        x = np.linspace(self.scale_x.min, self.scale_x.max, 100)
        w = wcs_sub.pixel_to_world_values(x)

        # Filter out NaN and Inf values
        w = w[np.isfinite(w)]
        lower = np.min(w)
        upper = np.max(w)

        # Find the tick positions
        tick_values_world, spacing = self.formatter_locator.locator(lower, upper)

        # Convert back to pixel coordinates
        tick_values = wcs_sub.world_to_pixel_values(tick_values_world)

        # Round tick_values to nearest int to avoid issues with dict lookup of
        # labels.
        # TODO: can we avoid this and make tick_labels more robust?
        tick_values = np.round(tick_values).astype(int).tolist()

        # Convert world coordinates to display units
        # TODO: right now we need to strip and add back the quantity-ness
        # because we can't rely just on astropy's unit conversion, we need to
        # use our own converter. For custom units, u.Unit may fail.
        converter = UnitConverter()
        tick_values_world = converter.to_unit(self.state.reference_data,
                                              self.state.reference_data.world_component_ids[self.state.x_att.axis],
                                              tick_values_world.value,
                                              self.state.x_display_unit) * u.Unit(self.state.x_display_unit)

        # Determine custom labels
        # TODO: determine how to do pretty formatting for exponential notation
        tick_labels = self.formatter_locator.formatter(tick_values_world, spacing)

        # Construct tick_labels dictionary
        tick_labels = dict(zip(tick_values, tick_labels))

        with self.axis_x.hold_sync():
            self.axis_x.tick_values = tick_values
            self.axis_x.tick_labels = tick_labels

    def _update_axes(self, *args):

        if self.state.x_att is not None:
            if self.state.x_display_unit:
                self.state.x_axislabel = str(self.state.x_att) + f' [{self.state.x_display_unit}]'
            else:
                self.state.x_axislabel = str(self.state.x_att)

        if self.state.normalize:
            self.state.y_axislabel = 'Normalized data values'
        else:
            if self.state.y_display_unit:
                self.state.y_axislabel = f'Data values [{self.state.y_display_unit}]'
            else:
                self.state.y_axislabel = 'Data values'

    def _roi_to_subset_state(self, roi):

        x = roi.to_polygon()[0]
        lo, hi = min(x), max(x)

        # Apply inverse unit conversion, converting from display to native units
        converter = UnitConverter()
        lo, hi = converter.to_native(self.state.reference_data,
                                     self.state.x_att, np.array([lo, hi]),
                                     self.state.x_display_unit)

        roi_new = RangeROI(min=lo, max=hi, orientation='x')

        return roi_to_subset_state(roi_new, x_att=self.state.x_att)
