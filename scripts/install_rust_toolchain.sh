#!/bin/bash

# latest version is '1.68.0' at time of writing
VERSION=${1}

# install the rust manager script
curl https://sh.rustup.rs -sSf | sh -s -- -y

# install a particular version
rustup install ${VERSION}

# print the new rust version info
cargo --version