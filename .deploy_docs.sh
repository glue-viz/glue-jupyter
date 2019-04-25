#!/bin/bash

set -evax

if [[ $TRAVIS_PULL_REQUEST == false && $TRAVIS_BRANCH == master && $TRAVIS_OS_NAME == linux && $PYTHON_VERSION == 3.7 ]]; then

    # Decrypt ssh deploy key
    openssl aes-256-cbc -K $encrypted_4288ce07de63_key -iv $encrypted_4288ce07de63_iv -in .deploy_docs_key.enc -out ~/.ssh/publish-key -d
    chmod u=rw,og= ~/.ssh/publish-key
    echo "Host github.com" >> ~/.ssh/config
    echo "  IdentityFile ~/.ssh/publish-key" >> ~/.ssh/config

    # Remember repository directory
    base_dir=$(pwd)

    # Clone the gh-pages branch of the repo in a temporary directory
    cd ..
    git clone --branch gh-pages git@github.com:glue-viz/glue-jupyter glue-jupyter-docs
    cd glue-jupyter-docs

    # Copy over built docs
    rsync -avz --delete --exclude .git/ $base_dir/docs/_build/html/ ./
    
    # Create nojekyll file so that _* folders work
    touch .nojekyll

    # Commit changes
    git --version
    git config --global user.name "Travis CI"
    git config --global user.email "travis@travis.ci"
    git add -A
    git commit --allow-empty -m "Update rendered docs to ""$TRAVIS_COMMIT"
    git push origin gh-pages

fi
