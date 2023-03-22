#!/bin/bash

# https://docs.adacore.com/gnat_ugn-docs/html/gnat_ugn/gnat_ugn/building_executable_programs_with_gnat.html

# available version is '10.1' at time of writing
VERSION=${1}

# install dependencies for script
sudo apt install -y \
    gnat=${VERSION}*;

# print the gnatmake version
gnatmake --version;