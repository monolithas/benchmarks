#!/bin/bash

# available version is '12.1' at time of writing
VERSION=${1}
NAME=gcc-${VERSION%%.*}

# install dependencies for script
sudo apt install -y \
    ${NAME}=${VERSION}*;

# print the gcc version
${NAME} --version;