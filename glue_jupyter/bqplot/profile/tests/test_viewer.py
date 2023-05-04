from astropy.wcs import WCS

import numpy as np
from numpy.testing import assert_allclose, assert_equal

from astropy import units as u

from glue.core import Data
from glue.core.roi import XRangeROI
from glue.config import unit_converter, settings
from glue.plugins.wcs_autolinking.wcs_autolinking import WCSLink


def setup_function(func):
    func.ORIGINAL_UNIT_CONVERTER = settings.UNIT_CONVERTER


def teardown_function(func):
    settings.UNIT_CONVERTER = func.ORIGINAL_UNIT_CONVERTER


def teardown_module():
    unit_converter._members.pop('test-spectral')


def test_non_hex_colors(app, dataxyz):

    # Make sure non-hex colors such as '0.4' and 'red', which are valid
    # matplotlib colors, work as expected.

    viewer = app.profile1d(data=dataxyz)
    dataxyz.style.color = '0.3'
    dataxyz.style.color = 'indigo'

    app.subset('test', dataxyz.id['x'] > 1)
    viewer.layer_options.selected = 1
    dataxyz.subsets[0].style.color = '0.5'
    dataxyz.subsets[0].style.color = 'purple'


def test_remove(app, data_image, data_volume):
    s = app.profile1d(data=data_image)
    s.add_data(data_volume)
    app.data_collection.new_subset_group(subset_state=data_image.id['intensity'] > 1, label='test')
    assert len(s.figure.marks) == 4
    s.remove_data(data_image)
    assert len(s.figure.marks) == 2
    s.remove_data(data_volume)
    assert len(s.figure.marks) == 0


@unit_converter('test-spectral')
class SpectralUnitConverter:

    def equivalent_units(self, data, cid, units):
        return map(str, u.Unit(units).find_equivalent_units(include_prefix_units=True,
                                                            equivalencies=u.spectral()))

    def to_unit(self, data, cid, values, original_units, target_units):
        return (values * u.Unit(original_units)).to_value(target_units,
                                                          equivalencies=u.spectral())


def test_unit_conversion(app):

    settings.UNIT_CONVERTER = 'test-spectral'

    wcs1 = WCS(naxis=1)
    wcs1.wcs.ctype = ['FREQ']
    wcs1.wcs.crval = [1]
    wcs1.wcs.cdelt = [1]
    wcs1.wcs.crpix = [1]
    wcs1.wcs.cunit = ['GHz']

    d1 = Data(f1=[1, 2, 3])
    d1.get_component('f1').units = 'Jy'
    d1.coords = wcs1

    wcs2 = WCS(naxis=1)
    wcs2.wcs.ctype = ['WAVE']
    wcs2.wcs.crval = [10]
    wcs2.wcs.cdelt = [10]
    wcs2.wcs.crpix = [1]
    wcs2.wcs.cunit = ['cm']

    d2 = Data(f2=[2000, 1000, 3000])
    d2.get_component('f2').units = 'mJy'
    d2.coords = wcs2

    session = app.session

    data_collection = session.data_collection
    data_collection.append(d1)
    data_collection.append(d2)
    data_collection.add_link(WCSLink(d1, d2))

    viewer = app.profile1d(data=d1)
    viewer.add_data(d2)

    assert viewer.layers[0].enabled
    assert viewer.layers[1].enabled

    x, y = viewer.state.layers[0].profile
    assert_allclose(x, [1.e9, 2.e9, 3.e9])
    assert_allclose(y, [1, 2, 3])

    x, y = viewer.state.layers[1].profile
    assert_allclose(x, 299792458 / np.array([0.1, 0.2, 0.3]))
    assert_allclose(y, [2000, 1000, 3000])

    assert viewer.state.x_min == 1.e9
    assert viewer.state.x_max == 3.e9
    assert viewer.state.y_min == 1.
    assert viewer.state.y_max == 3.

    roi = XRangeROI(1.4e9, 2.1e9)
    viewer.apply_roi(roi)

    assert len(d1.subsets) == 1
    assert_equal(d1.subsets[0].to_mask(), [0, 1, 0])

    assert len(d2.subsets) == 1
    assert_equal(d2.subsets[0].to_mask(), [0, 1, 0])

    viewer.state.x_display_unit = 'GHz'
    viewer.state.y_display_unit = 'mJy'

    x, y = viewer.state.layers[0].profile
    assert_allclose(x, [1, 2, 3])
    assert_allclose(y, [1000, 2000, 3000])

    x, y = viewer.state.layers[1].profile
    assert_allclose(x, 2.99792458 / np.array([1, 2, 3]))
    assert_allclose(y, [2000, 1000, 3000])

    assert viewer.state.x_min == 1.
    assert viewer.state.x_max == 3.
    assert viewer.state.y_min == 1000.
    assert viewer.state.y_max == 3000.

    roi = XRangeROI(0.5, 1.2)
    viewer.apply_roi(roi)

    assert len(d1.subsets) == 1
    assert_equal(d1.subsets[0].to_mask(), [1, 0, 0])

    assert len(d2.subsets) == 1
    assert_equal(d2.subsets[0].to_mask(), [0, 0, 1])

    viewer.state.x_display_unit = 'cm'

    roi = XRangeROI(15, 35)
    viewer.apply_roi(roi)

    assert len(d1.subsets) == 1
    assert_equal(d1.subsets[0].to_mask(), [1, 0, 0])

    assert len(d2.subsets) == 1
    assert_equal(d2.subsets[0].to_mask(), [0, 1, 1])
