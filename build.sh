#!/bin/bash

# exit on error
set -e

# build python package
python -m build
# ensure public folder is present and copy python package
mkdir -p webgui/public/
cp dist/*.whl webgui/public/
# ensure js packages are available and run npm scripts
npm install
npm run $1
