#!/usr/bin/bash

set -e

docker build --build-arg UNAME=$(id -u -n) --build-arg UID=$(id -u) --build-arg GID=$(id -g) -t archsim .
docker run -it --rm --mount type=bind,source="$(pwd)",target=/usr/src/app/ -p 4173:4173 --user $(id -u):$(id -g) archsim ./build.sh preview-docker
