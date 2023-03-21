#!/bin/bash

# clear the tmp directory
rm -rf tmp/*;

# copy programs to tmp directory
cp programs/nbody/* tmp;

# copy the makefile to tmp directory
cp makefiles/ubuntu.22.04.make tmp;

cd tmp;

export RUST=rustc
export RUSTOPTS="-C opt-level=3 -C target-cpu=ivybridge -C codegen-units=1"

make --makefile=ubuntu.22.04.make nbody-rust-0.rust_run

# ./nbody-ada-0.ada_run 50000