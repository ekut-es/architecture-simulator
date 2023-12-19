#!/bin/bash

set -e

python -m build
mkdir -p webgui/public/
cp dist/*.whl webgui/public/
npm run $1
