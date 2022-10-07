How to release a new version of glue-jupyter
============================================

A new release of glue-jupyter is now almost fully automated.
For maintainers it should be nice and simple to do, especially if all merged PRs
have informative titles and are correctly labelled.

Here is the process to follow to create a new release:

* Go through all the PRs since the last release, make sure they have
  descriptive titles (as these will become the auto-generated changelog entries)
  and are labelled correctly - preferably identifying them as one of
  `bug`, `enhancement` or `documentation`.
* Go to the GitHub releases interface and draft a new release; new tags should
  include the trailing patch version `.0` on major.minor releases
  (releases prior to 0.11.0 didn't).
* Use the GitHub autochange log generator, this should use the configuration in
  `.github/release.yml` to make headings based on labels.
* Edit the draft release notes as required, particularly to call out major
  changes at the top.
* Publish the release.
* Have a beverage of your choosing. (Note that the wheels may take some time to
  build).
