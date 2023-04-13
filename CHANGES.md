# Full changelog

## v0.16.2 - 2023-04-13

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### Bug Fixes

- Allow cmap and size to take cateogricals by @jfoster17 in https://github.com/glue-viz/glue-jupyter/pull/347
- Don't overload _update_data in image viewer layer artist by @astrofrog in https://github.com/glue-viz/glue-jupyter/pull/350

#### Other Changes

- Remove pkg resources call by @jfoster17 in https://github.com/glue-viz/glue-jupyter/pull/348

**Full Changelog**: https://github.com/glue-viz/glue-jupyter/compare/v0.16.1...v0.16.2

## v0.16.1 - 2023-02-07

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### Bug Fixes

- Don't set scale limits if glue state limits are None by @astrofrog in https://github.com/glue-viz/glue-jupyter/pull/345

**Full Changelog**: https://github.com/glue-viz/glue-jupyter/compare/v0.16.0...v0.16.1

## v0.16.0 - 2023-02-03

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### Bug Fixes

- Fix updating of image viewer when data is modified by @astrofrog in https://github.com/glue-viz/glue-jupyter/pull/339
- Fix initial limits of viewers by @astrofrog in https://github.com/glue-viz/glue-jupyter/pull/344

#### New Features

- Initial support for unit conversion in profile viewer by @astrofrog in https://github.com/glue-viz/glue-jupyter/pull/311

#### Other Changes

- MNT: Replace zmq ioloop with tornado by @pllim in https://github.com/glue-viz/glue-jupyter/pull/343

**Full Changelog**: https://github.com/glue-viz/glue-jupyter/compare/v0.15.0...v0.16.0

## v0.15.0 - 2022-12-19

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### Bug Fixes

- Set row number column width in Table widget dynamically from no. of digits
- by @kecnry in https://github.com/glue-viz/glue-jupyter/pull/337
- Fix bug where empty histogram layer does not redraw by @Carifio24 in https://github.com/glue-viz/glue-jupyter/pull/338

#### New Features

- Allow empty `Data` to be loaded into the Table Viewer by @duytnguyendtn in https://github.com/glue-viz/glue-jupyter/pull/336
- Allow adjusting z-order for scatter and histogram layers by @Carifio24 in https://github.com/glue-viz/glue-jupyter/pull/334

#### Other Changes

- Corrected spelling errors by @jsoref in https://github.com/glue-viz/glue-jupyter/pull/333
- Updated `ipyvolume` and `scikit-image` requirements for numpy 1.24 compatibility
- by @dhomeier in https://github.com/glue-viz/glue-jupyter/pull/341

### New Contributors

- @jsoref made their first contribution in https://github.com/glue-viz/glue-jupyter/pull/333

**Full Changelog**: https://github.com/glue-viz/glue-jupyter/compare/v0.14.2...v0.15.0

## v0.14.2 - 2022-10-31

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

- Fix compatibility of image viewer with recent versions of glue-core by @astrofrog in https://github.com/glue-viz/glue-jupyter/pull/331

**Full Changelog**: https://github.com/glue-viz/glue-jupyter/compare/v0.14.1...v0.14.2

## v0.14.1 - 2022-10-26

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### Bug Fixes

- If image is not used in scatter layer, use an empty image. by @maartenbreddels in https://github.com/glue-viz/glue-jupyter/pull/324
- Avoid sending any unnecessary updates to the front-end and prevent hanging due to circular callbacks by @astrofrog in https://github.com/glue-viz/glue-jupyter/pull/325
- Fix support for all `BaseCartesianData` subclass instances by @astrofrog in https://github.com/glue-viz/glue-jupyter/pull/327
- Fix `IndexError` that occurred in some cases during JSON to State translation by @astrofrog in https://github.com/glue-viz/glue-jupyter/pull/326

#### Other Changes

- Updated dependencies to run and test with Python 3.11 by @dhomeier in https://github.com/glue-viz/glue-jupyter/pull/329

**Full Changelog**: https://github.com/glue-viz/glue-jupyter/compare/v0.14.0...v0.14.1

## v0.14.0 - 2022-10-10

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### New Features

- Added a setting to control disabling of tools in other viewers by @astrofrog in https://github.com/glue-viz/glue-jupyter/pull/320

**Full Changelog**: https://github.com/glue-viz/glue-jupyter/compare/v0.13.1...v0.14.0

## [0.13.1](https://github.com/glue-viz/glue-jupyter/compare/v0.13.0...v0.13.1) - 2022-09-26

### What's Changed

#### Bug Fixes

- Fixed a bug causing the colour picker to enter an infinite loop upon
- dragging in the widget. in https://github.com/glue-viz/glue-jupyter/pull/312
- 
- Ensure `bqplot` `FRBImage` sends data as float32 to WebGL. in https://github.com/glue-viz/glue-jupyter/pull/318, https://github.com/glue-viz/glue-jupyter/pull/319
- 

## [0.13.0](https://github.com/glue-viz/glue-jupyter/compare/v0.12.1...v0.13.0) - 2022-08-26

### New Features

- Add button to profile viewer layers to toggle plotting as steps. in https://github.com/glue-viz/glue-jupyter/pull/309

## [0.12.1](https://github.com/glue-viz/glue-jupyter/compare/v0.12.0...v0.12.1) - 2022-07-29

- Fixed a bug that caused the image viewer zoom to be reset when adding
- additional datasets. in https://github.com/glue-viz/glue-jupyter/pull/316

## [0.12.0](https://github.com/glue-viz/glue-jupyter/compare/v0.11.4...v0.12.0) - 2022-04-07

- Speed up syncing of glue and bqplot limits in viewers. in https://github.com/glue-viz/glue-jupyter/pull/306
- 
- Improve performance of line plots using WebGL. in https://github.com/glue-viz/glue-jupyter/pull/227
- 

## [0.11.4](https://github.com/glue-viz/glue-jupyter/compare/v0.11.3...v0.11.4) - 2022-03-31

- Fixed compatibility with latest developer version of bqplot. in https://github.com/glue-viz/glue-jupyter/pull/302
- 
- Fixed a bug that caused numbers in exponential notation (e.g. 1e2) to
- be reformatted immediately to decimal form (e.g. 100). in https://github.com/glue-viz/glue-jupyter/pull/303
- 

## [0.11.3](https://github.com/glue-viz/glue-jupyter/compare/v0.11.2...v0.11.3) - 2022-03-29

- Fixed a bug that caused clicking and dragging of existing regions to not
- correctly restore other event. in https://github.com/glue-viz/glue-jupyter/pull/301

## [0.11.2](https://github.com/glue-viz/glue-jupyter/compare/v0.11.1...v0.11.2) - 2022-03-22

- Improvements to vue layout, prevent long content from pushing out of view. in https://github.com/glue-viz/glue-jupyter/pull/299

## [0.11.1](https://github.com/glue-viz/glue-jupyter/compare/v0.11.0...v0.11.1) - 2022-03-03

- Fix a bug where removing a callback function from the events dict was
- pop()ing a wrong key. in https://github.com/glue-viz/glue-jupyter/pull/296

## [0.11.0](https://github.com/glue-viz/glue-jupyter/compare/v0.10.1...v0.11.0) - 2022-02-24

- Only trigger bqplot viewer callbacks on their specified events. in https://github.com/glue-viz/glue-jupyter/pull/279
- 
- Link opacity of the histogram bars with the layer state in
- the histogram viewer. in https://github.com/glue-viz/glue-jupyter/pull/275
- 
- Fix a bug that caused the data and subset colors and labels to not be
- updated the active subset dropdown and the layer selection dropdown. in https://github.com/glue-viz/glue-jupyter/pull/283
- 
- Fix a bug that caused out of bounds error on subset deletion when
- viewer shape is zero after the viewer has been destroyed by an
- application. in https://github.com/glue-viz/glue-jupyter/pull/293
- 
- Fix a bug that caused the eye icon to not be updated when toggling
- the visibility of a layer. in https://github.com/glue-viz/glue-jupyter/pull/289
- 
- Add the ability to set fill attribute for scatter plot. in https://github.com/glue-viz/glue-jupyter/pull/292
- 
- Add the ability to make the table viewer scrollable. in https://github.com/glue-viz/glue-jupyter/pull/287
- 

## [0.10.1](https://github.com/glue-viz/glue-jupyter/compare/v0.10...v0.10.1) - 2021-09-16

- Prevent jumping around of view in profile viewer when creating
- or updating subsets. in https://github.com/glue-viz/glue-jupyter/pull/247

## [0.10](https://github.com/glue-viz/glue-jupyter/compare/v0.9...v0.10) - 2021-09-14

- Add the ability to hide columns in the table viewer by using
- `TableViewer.state.hidden_components`. in https://github.com/glue-viz/glue-jupyter/pull/259

## [0.9](https://github.com/glue-viz/glue-jupyter/compare/v0.8.1...v0.9) - 2021-09-14

- Add an option to allow fixed resolution buffer to be larger than
- axes by a given factor. in https://github.com/glue-viz/glue-jupyter/pull/246

## [0.8.1](https://github.com/glue-viz/glue-jupyter/compare/v0.8...v0.8.1) - 2021-09-07

- Better handle incompatible subsets in table viewer. in https://github.com/glue-viz/glue-jupyter/pull/256
- 
- Better handle case where image artist has already been removed. in https://github.com/glue-viz/glue-jupyter/pull/256
- 

## [0.8](https://github.com/glue-viz/glue-jupyter/compare/v0.7...v0.8) - 2021-08-20

- Fix compatibility with latest stable releases of `glue-core`. in https://github.com/glue-viz/glue-jupyter/pull/252
- 
- Fix updating of layer list when adding new layers to a figure. in https://github.com/glue-viz/glue-jupyter/pull/251
- 
- Avoid updating `FRBMark` multiple times when adding a new layer. in https://github.com/glue-viz/glue-jupyter/pull/248
- 
- Improve tooltip for pan/zoom. in https://github.com/glue-viz/glue-jupyter/pull/245
- 

## [0.7](https://github.com/glue-viz/glue-jupyter/compare/v0.6.1...v0.7) - 2021-07-02

- Add implementation of an elliptical selection (not yet exposed in the default
- viewers). in https://github.com/glue-viz/glue-jupyter/pull/241, in https://github.com/glue-viz/glue-jupyter/pull/242
- 
- Disable tools in viewers when a tool is selected in another viewer, and add
- a setting to allow the subset selector to revert back to 'Create New' each time
- a new tool is selected. in https://github.com/glue-viz/glue-jupyter/pull/238
- 

## [0.6.1](https://github.com/glue-viz/glue-jupyter/compare/v0.6...v0.6.1) - 2021-06-10

- Fix bug that caused selection tools to not work correctly in 0.6 release. in https://github.com/glue-viz/glue-jupyter/pull/235
- 
- Fix bug that caused the aspect ratio of the image viewer to change when a
- selection region was partially outside plot. in https://github.com/glue-viz/glue-jupyter/pull/233
- 

## [0.6](https://github.com/glue-viz/glue-jupyter/compare/v0.5...v0.6) - 2021-06-08

- Add class name to `subset_select` vue component for CSS customization. in https://github.com/glue-viz/glue-jupyter/pull/226
- 
- Use SVG icons instead of PNG for toolbar. in https://github.com/glue-viz/glue-jupyter/pull/228
- 
- Make sure image viewer fills all available space even when using
- equal aspect ratio. in https://github.com/glue-viz/glue-jupyter/pull/231
- 

## [0.5](https://github.com/glue-viz/glue-jupyter/compare/v0.4...v0.5) - 2021-05-13

- Fix toolbar when non-checkable tools were present. in https://github.com/glue-viz/glue-jupyter/pull/222
- 
- Allow tool icons to be specified as paths instead of just names. in https://github.com/glue-viz/glue-jupyter/pull/225
- 

## [0.4](https://github.com/glue-viz/glue-jupyter/compare/v0.3...v0.4) - 2021-04-28

- Added a new 'home' tool in bqplot viewers to reset limits. in https://github.com/glue-viz/glue-jupyter/pull/218
- 
- Fixed an issue which caused circular selections to be represented
- by `EllipticalROI` instead of `CircularROI` in some corner
- cases. in https://github.com/glue-viz/glue-jupyter/pull/217
- 

## [0.3](https://github.com/glue-viz/glue-jupyter/compare/v0.2.2...v0.3) - 2021-04-15

- Fixed implementation of `JupyterApplication.viewers` to now return
- list of viewers as opposed to empty list. in https://github.com/glue-viz/glue-jupyter/pull/214
- 
- Add the ability to register callback functions for mouse and keyboard
- events with the bqplot viewers. in https://github.com/glue-viz/glue-jupyter/pull/213
- 

## [0.2.2](https://github.com/glue-viz/glue-jupyter/compare/v0.2.1...v0.2.2) - 2021-03-18

- Fixed slices slider in image viewer which under certain conditions
- changed the state when an empty slices property was received. in https://github.com/glue-viz/glue-jupyter/pull/211
- 
- Fixed a bug that caused the image percentile value to not have any
- effect. in https://github.com/glue-viz/glue-jupyter/pull/208
- 

## [0.2.1](https://github.com/glue-viz/glue-jupyter/compare/v0.2...v0.2.1) - 2020-09-21

- Fixed a bug with removing contour layers. in https://github.com/glue-viz/glue-jupyter/pull/204

## [0.2](https://github.com/glue-viz/glue-jupyter/compare/v0.1...v0.2) - 2020-09-17

- De-select selection tools after a selection has been made. in https://github.com/glue-viz/glue-jupyter/pull/164
- 
- Removed ipymaterialui widgets and fix cases where these widgets were
- used over ipyvuetify widgets. in https://github.com/glue-viz/glue-jupyter/pull/143
- 
- Make the 'allow multiple subsets' button optional and disabled by
- default. in https://github.com/glue-viz/glue-jupyter/pull/163
- 
- Fixed a bug that caused profiles of subsets to not be hidden if an
- existing subset was emptied. in https://github.com/glue-viz/glue-jupyter/pull/162
- 
- Fixed a bug that caused exceptions when trying to remove data from
- bqplot viewers. in https://github.com/glue-viz/glue-jupyter/pull/166
- 
- Added circular selection to scatter and image viewer. in https://github.com/glue-viz/glue-jupyter/pull/165
- 
- Make sure glue plugins are loaded when calling `jglue`. in https://github.com/glue-viz/glue-jupyter/pull/171
- 
- Make it possible to remove subsets from the UI. in https://github.com/glue-viz/glue-jupyter/pull/169
- 
- Implement click-and-drag for selections in image viewer. in https://github.com/glue-viz/glue-jupyter/pull/170
- 
- Fixed behavior of equal aspect ratio in image viewer. in https://github.com/glue-viz/glue-jupyter/pull/184
- 
- Fixed a bug that caused the image viewer to raise an error when changing
- the reference data from a 3-d to a 2-d dataset. in https://github.com/glue-viz/glue-jupyter/pull/188
- 
- Fixed a bug that caused profiles to not be shown in the profile viewer
- when changing the reference data. in https://github.com/glue-viz/glue-jupyter/pull/188
- 

## [0.1](https://github.com/glue-viz/glue-jupyter/releases/tag/v0.1) - 2020-01-08

- Initial version.
