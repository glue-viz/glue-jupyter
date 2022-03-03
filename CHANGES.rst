0.11.1 (2022-03-03)
===================

* Fix a bug where removing a callback function from the events dict was
  pop()ing a wrong key. [#296]

0.11.0 (2022-02-24)
===================

* Only trigger bqplot viewer callbacks on their specified events. [#279]

* Link opacity of the histogram bars with the layer state in
  the histogram viewer. [#275]

* Fix a bug that caused the data and subset colors and labels to not be
  updated the active subset dropdown and the layer selection dropdown.
  [#283]

* Fix a bug that caused out of bounds error on subset deletion when
  viewer shape is zero after the viewer has been destroyed by an
  application. [#293]

* Fix a bug that caused the eye icon to not be updated when toggling
  the visibility of a layer. [#289]

* Add the ability to set fill attribute for scatter plot. [#292]

* Add the ability to make the table viewer scrollable. [#287]

0.10.1 (2021-09-16)
===================

* Prevent jumping around of view in profile viewer when creating
  or updating subsets. [#247]

0.10 (2021-09-14)
=================

* Add the ability to hide columns in the table viewer by using
  ``TableViewer.state.hidden_components``. [#259]

0.9 (2021-09-14)
================

* Add an option to allow fixed resolution buffer to be larger than
  axes by a given factor. [#246]

0.8.1 (2021-09-07)
==================

* Better handle incompatible subsets in table viewer. [#256]

* Better handle case where image artist has already been removed. [#256]

0.8 (2021-08-20)
================

* Fix compatibility with latest stable releases of glue-core. [#252]

* Fix updating of layer list when adding new layers to a figure. [#251]

* Avoid updating FRBMark multiple times when adding a new layer. [#248]

* Improve tooltip for pan/zoom. [#245]

0.7 (2021-07-02)
================

* Add implementation of an elliptical selection (not yet exposed in the default
  viewers). [#241, #242]

* Disable tools in viewers when a tool is selected in another viewer, and add
  a setting to allow the subset selector to revert back to 'Create New' each time
  a new tool is selected. [#238]

0.6.1 (2021-06-10)
==================

* Fix bug that caused selection tools to not work correctly in 0.6 release. [#235]

* Fix bug that caused the aspect ratio of the image viewer to change when a
  selection region was partially outside plot. [#233]

0.6 (2021-06-08)
================

* Add class name to subset_select vue component for CSS customization. [#226]

* Use SVG icons instead of PNG for toolbar. [#228]

* Make sure image viewer fills all available space even when using
  equal aspect ratio. [#231]

0.5 (2021-05-13)
================

* Fix toolbar when non-checkable tools were present. [#222]

* Allow tool icons to be specified as paths instead of just names. [#225]

0.4 (2021-04-28)
================

* Added a new 'home' tool in bqplot viewers to reset limits. [#218]

* Fixed an issue which caused circular selections to be represented
  by ``EllipticalROI`` instead of ``CircularROI`` in some corner
  cases. [#217]

0.3 (2021-04-15)
================

* Fixed implementation of ``JupyterApplication.viewers`` to now return
  list of viewers as opposed to empty list. [#214]

* Add the ability to register callback functions for mouse and keyboard
  events with the bqplot viewers. [#213]

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
