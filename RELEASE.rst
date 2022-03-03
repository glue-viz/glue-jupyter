How to release a new version of glue-jupyter
============================================

#. Edit the ``CHANGES.rst`` file to add the release date for the release
   you want to make and make sure the changelog is complete.

#. Commit the changes using::

    git commit -m "Preparing release v..."

   where v... is the version you are releasing and push to main::

    git push upstream main

#. Tag the release you want to make, optionally signing it (``-s``)::

    git tag -m v0.2.2 v0.2.2

   and push the tag::

    git push upstream v0.2.2

#. At this point, the release sdist and wheel will be built on Azure
   Pipelines and automatically uploaded to PyPI. You can check
   the build `here <https://dev.azure.com/glue-viz/glue-jupyter/_build?definitionId=7>`_
   and if there are any issues you can delete the tag, fix the issues
   (preferably via a pull request) and then try the release process
   again.
