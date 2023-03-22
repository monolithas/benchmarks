#!/bin/bash

NAME=rayon
VERSION=1.7.0

mkdir -p tmp data/dependencies/rust

rm -rf tmp;
cargo new tmp;

cd tmp;

cargo add ${NAME}@${VERSION};
cargo build --release;

cp target/release/deps/* ../data/dependencies/rust/

cd ..;
rm -rf tmp/*