#!/bin/bash

# exit on error
set -e

# build python package
python -m build
# ensure custom markers are present in the svg
python build_svg.py
# ensure js packages are available and run npm scripts
npm install

if [ "$1" = "preview*" ]; then
    npm run build
fi
npm run $1
