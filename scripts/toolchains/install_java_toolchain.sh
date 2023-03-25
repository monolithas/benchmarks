#!/bin/bash

# available version is '19' at time of writing
VERSION=${1}
NAME=openjdk-${VERSION%%.*}-jdk

# install dependencies for script and benchmarks
sudo apt install -y \
    ${NAME};

# print the javac version
javac --version;