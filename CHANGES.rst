0.2.2 (2021-03-18)
==================

* Fixed slices slider in image viewer which under certain conditions
  changed the state when an empty slices property was received. [#211]

* Fixed a bug that caused the image percentile value to not have any
  effect. [#208]

0.2.1 (2020-09-21)
==================

* Fixed a bug with removing contour layers. [#204]

0.2 (2020-09-17)
================

* De-select selection tools after a selection has been made. [#164]

* Removed ipymaterialui widgets and fix cases where these widgets were
  used over ipyvuetify widgets. [#143]

* Make the 'allow multiple subsets' button optional and disabled by
  default. [#163]

* Fixed a bug that caused profiles of subsets to not be hidden if an
  existing subset was emptied. [#162]

* Fixed a bug that caused exceptions when trying to remove data from
  bqplot viewers. [#166]

* Added circular selection to scatter and image viewer. [#165]

* Make sure glue plugins are loaded when calling ``jglue``. [#171]

* Make it possible to remove subsets from the UI. [#169]

* Implement click-and-drag for selections in image viewer. [#170]

* Fixed behavior of equal aspect ratio in image viewer. [#184]

* Fixed a bug that caused the image viewer to raise an error when changing
  the reference data from a 3-d to a 2-d dataset. [#188]

* Fixed a bug that caused profiles to not be shown in the profile viewer
  when changing the reference data. [#188]

0.1 (2020-01-08)
================

* Initial version.
