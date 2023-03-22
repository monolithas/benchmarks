#!/bin/bash

# available version is '12.1' at time of writing
VERSION=${1}
NAME=gcc-${VERSION%%.*}

# install dependencies for script and benchmarks
sudo apt install -y \
    libomp-dev      \
    ${NAME}=${VERSION}*;

# print the gcc version
${NAME} --version;