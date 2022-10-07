# Full changelog

## [unreleased](https://github.com/glue-viz/glue-jupyter/compare/v0.13.1...HEAD)

## [0.13.1](https://github.com/glue-viz/glue-jupyter/compare/v0.13.0...0.13.1) (2022-09-26)

### What's Changed

#### Bug Fixes

- Fixed a bug causing the colour picker to enter an infinite loop upon
  dragging in the widget. https://github.com/glue-viz/glue-jupyter/pull/312

- Ensure ``bqplot`` ``FRBImage`` sends data as float32 to WebGL. https://github.com/glue-viz/glue-jupyter/pull/318, https://github.com/glue-viz/glue-jupyter/pull/319

**Full Changelog**: https://github.com/glue-viz/glue-jupyter/compare/v0.13.0...v0.13.1

## [0.13.0](https://github.com/glue-viz/glue-jupyter/compare/v0.12.1...v0.13.0) (2022-08-26)

### New Features

- Add button to profile viewer layers to toggle plotting as steps. https://github.com/glue-viz/glue-jupyter/pull/309

**Full Changelog**: https://github.com/glue-viz/glue-jupyter/compare/v0.12.0...v0.13.0

## [0.12.1](https://github.com/glue-viz/glue-jupyter/compare/v0.12.0...0.12.1) (2022-07-29)

- Fixed a bug that caused the image viewer zoom to be reset when adding
  additional datasets. https://github.com/glue-viz/glue-jupyter/pull/316

## [0.12.0](https://github.com/glue-viz/glue-jupyter/compare/v0.11.4...0.12.0) (2022-04-07)

- Speed up syncing of glue and bqplot limits in viewers. https://github.com/glue-viz/glue-jupyter/pull/306

- Improve performance of line plots using WebGL. https://github.com/glue-viz/glue-jupyter/pull/227

**Full Changelog**: https://github.com/glue-viz/glue-jupyter/compare/v0.11.0...v0.12.0

## [0.11.4](https://github.com/glue-viz/glue-jupyter/compare/v0.11.3...0.11.4) (2022-03-31)

- Fixed compatibility with latest developer version of bqplot. https://github.com/glue-viz/glue-jupyter/pull/302

- Fixed a bug that caused numbers in exponential notation (e.g. 1e2) to
  be reformatted immediately to decimal form (e.g. 100). https://github.com/glue-viz/glue-jupyter/pull/303

## [0.11.3](https://github.com/glue-viz/glue-jupyter/compare/v0.11.2...0.11.3) (2022-03-29)

- Fixed a bug that caused clicking and dragging of existing regions to not
  correctly restore other event. https://github.com/glue-viz/glue-jupyter/pull/301

## [0.11.2](https://github.com/glue-viz/glue-jupyter/compare/v0.11.1...0.11.2) (2022-03-22)

- Improvements to vue layout, prevent long content from pushing out of view. https://github.com/glue-viz/glue-jupyter/pull/299

## [0.11.1](https://github.com/glue-viz/glue-jupyter/compare/v0.11.0...0.11.1) (2022-03-03)

- Fix a bug where removing a callback function from the events dict was
  pop()ing a wrong key. https://github.com/glue-viz/glue-jupyter/pull/296

## [0.11.0](https://github.com/glue-viz/glue-jupyter/compare/v0.10.1...0.11.0) (2022-02-24)

- Only trigger bqplot viewer callbacks on their specified events. https://github.com/glue-viz/glue-jupyter/pull/279

- Link opacity of the histogram bars with the layer state in
  the histogram viewer. https://github.com/glue-viz/glue-jupyter/pull/275

- Fix a bug that caused the data and subset colors and labels to not be
  updated the active subset dropdown and the layer selection dropdown.
  https://github.com/glue-viz/glue-jupyter/pull/283

- Fix a bug that caused out of bounds error on subset deletion when
  viewer shape is zero after the viewer has been destroyed by an
  application. https://github.com/glue-viz/glue-jupyter/pull/293

- Fix a bug that caused the eye icon to not be updated when toggling
  the visibility of a layer. https://github.com/glue-viz/glue-jupyter/pull/289

- Add the ability to set fill attribute for scatter plot. https://github.com/glue-viz/glue-jupyter/pull/292

- Add the ability to make the table viewer scrollable. https://github.com/glue-viz/glue-jupyter/pull/287

## [0.10.1](https://github.com/glue-viz/glue-jupyter/compare/v0.10...0.10.1) (2021-09-16)

- Prevent jumping around of view in profile viewer when creating
  or updating subsets. https://github.com/glue-viz/glue-jupyter/pull/247

## [0.10](https://github.com/glue-viz/glue-jupyter/compare/v0.9...0.10) (2021-09-14)

- Add the ability to hide columns in the table viewer by using
  ``TableViewer.state.hidden_components``. https://github.com/glue-viz/glue-jupyter/pull/259

## [0.9](https://github.com/glue-viz/glue-jupyter/compare/v0.8.1...0.9) (2021-09-14)

- Add an option to allow fixed resolution buffer to be larger than
  axes by a given factor. https://github.com/glue-viz/glue-jupyter/pull/246

## [0.8.1](https://github.com/glue-viz/glue-jupyter/compare/v0.8...0.8.1) (2021-09-07)

- Better handle incompatible subsets in table viewer. https://github.com/glue-viz/glue-jupyter/pull/256

- Better handle case where image artist has already been removed. https://github.com/glue-viz/glue-jupyter/pull/256

## [0.8](https://github.com/glue-viz/glue-jupyter/compare/v0.7...0.8) (2021-08-20)

- Fix compatibility with latest stable releases of ``glue-core``. https://github.com/glue-viz/glue-jupyter/pull/252

- Fix updating of layer list when adding new layers to a figure. https://github.com/glue-viz/glue-jupyter/pull/251

- Avoid updating ``FRBMark`` multiple times when adding a new layer. https://github.com/glue-viz/glue-jupyter/pull/248

- Improve tooltip for pan/zoom. https://github.com/glue-viz/glue-jupyter/pull/245

## [0.7](https://github.com/glue-viz/glue-jupyter/compare/v0.6.1...0.7) (2021-07-02)

- Add implementation of an elliptical selection (not yet exposed in the default
  viewers). https://github.com/glue-viz/glue-jupyter/pull/241, https://github.com/glue-viz/glue-jupyter/pull/242

- Disable tools in viewers when a tool is selected in another viewer, and add
  a setting to allow the subset selector to revert back to 'Create New' each time
  a new tool is selected. https://github.com/glue-viz/glue-jupyter/pull/238

## [0.6.1](https://github.com/glue-viz/glue-jupyter/compare/v0.6...0.6.1) (2021-06-10)

- Fix bug that caused selection tools to not work correctly in 0.6 release. https://github.com/glue-viz/glue-jupyter/pull/235

- Fix bug that caused the aspect ratio of the image viewer to change when a
  selection region was partially outside plot. https://github.com/glue-viz/glue-jupyter/pull/233

## [0.6](https://github.com/glue-viz/glue-jupyter/compare/v0.5...0.6) (2021-06-08)

- Add class name to ``subset_select`` vue component for CSS customization. https://github.com/glue-viz/glue-jupyter/pull/226

- Use SVG icons instead of PNG for toolbar. https://github.com/glue-viz/glue-jupyter/pull/228

- Make sure image viewer fills all available space even when using
  equal aspect ratio. https://github.com/glue-viz/glue-jupyter/pull/231

## [0.5](https://github.com/glue-viz/glue-jupyter/compare/v0.4...0.5) (2021-05-13)

- Fix toolbar when non-checkable tools were present. https://github.com/glue-viz/glue-jupyter/pull/222

- Allow tool icons to be specified as paths instead of just names. https://github.com/glue-viz/glue-jupyter/pull/225

## [0.4](https://github.com/glue-viz/glue-jupyter/compare/v0.3...0.4) (2021-04-28)

- Added a new 'home' tool in bqplot viewers to reset limits. https://github.com/glue-viz/glue-jupyter/pull/218

- Fixed an issue which caused circular selections to be represented
  by ``EllipticalROI`` instead of ``CircularROI`` in some corner
  cases. https://github.com/glue-viz/glue-jupyter/pull/217

## [0.3](https://github.com/glue-viz/glue-jupyter/compare/v0.2.2...0.3) (2021-04-15)

- Fixed implementation of ``JupyterApplication.viewers`` to now return
  list of viewers as opposed to empty list. https://github.com/glue-viz/glue-jupyter/pull/214

- Add the ability to register callback functions for mouse and keyboard
  events with the bqplot viewers. https://github.com/glue-viz/glue-jupyter/pull/213

## [0.2.2](https://github.com/glue-viz/glue-jupyter/compare/v0.2.1...0.2.2) (2021-03-18)

- Fixed slices slider in image viewer which under certain conditions
  changed the state when an empty slices property was received. https://github.com/glue-viz/glue-jupyter/pull/211

- Fixed a bug that caused the image percentile value to not have any
  effect. https://github.com/glue-viz/glue-jupyter/pull/208

## [0.2.1](https://github.com/glue-viz/glue-jupyter/compare/v0.2...0.2.1) (2020-09-21)

- Fixed a bug with removing contour layers. https://github.com/glue-viz/glue-jupyter/pull/204

## [0.2](https://github.com/glue-viz/glue-jupyter/compare/v0.1...0.2) (2020-09-17)

- De-select selection tools after a selection has been made. https://github.com/glue-viz/glue-jupyter/pull/164

- Removed ipymaterialui widgets and fix cases where these widgets were
  used over ipyvuetify widgets. https://github.com/glue-viz/glue-jupyter/pull/143

- Make the 'allow multiple subsets' button optional and disabled by
  default. https://github.com/glue-viz/glue-jupyter/pull/163

- Fixed a bug that caused profiles of subsets to not be hidden if an
  existing subset was emptied. https://github.com/glue-viz/glue-jupyter/pull/162

- Fixed a bug that caused exceptions when trying to remove data from
  bqplot viewers. https://github.com/glue-viz/glue-jupyter/pull/166

- Added circular selection to scatter and image viewer. https://github.com/glue-viz/glue-jupyter/pull/165

- Make sure glue plugins are loaded when calling ``jglue``. https://github.com/glue-viz/glue-jupyter/pull/171

- Make it possible to remove subsets from the UI. https://github.com/glue-viz/glue-jupyter/pull/169

- Implement click-and-drag for selections in image viewer. https://github.com/glue-viz/glue-jupyter/pull/170

- Fixed behavior of equal aspect ratio in image viewer. https://github.com/glue-viz/glue-jupyter/pull/184

- Fixed a bug that caused the image viewer to raise an error when changing
  the reference data from a 3-d to a 2-d dataset. https://github.com/glue-viz/glue-jupyter/pull/188

- Fixed a bug that caused profiles to not be shown in the profile viewer
  when changing the reference data. https://github.com/glue-viz/glue-jupyter/pull/188

## [0.1](https://github.com/glue-viz/glue-jupyter/releases/tag/v0.1) (2020-01-08)

- Initial version.
