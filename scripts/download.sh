#!/bin/bash

# remove existing programs and dependencies
poetry run clean -- --targets programs dependencies output

poetry run fetch -- -r=3 -n="nbody-rust-1"
poetry run fetch -- -r=3 -n="nbody-rust-2"
poetry run fetch -- -r=3 -n="nbody-rust-3"
poetry run fetch -- -r=3 -n="nbody-rust-4"
poetry run fetch -- -r=3 -n="nbody-gpp-1"
poetry run fetch -- -r=3 -n="nbody-gpp-2"
poetry run fetch -- -r=3 -n="nbody-gpp-3"
poetry run fetch -- -r=3 -n="nbody-gcc-1"
poetry run fetch -- -r=3 -n="nbody-gcc-2"
poetry run fetch -- -r=3 -n="nbody-gcc-3"
poetry run fetch -- -r=3 -n="nbody-gcc-4"
poetry run fetch -- -r=3 -n="nbody-gcc-7"
poetry run fetch -- -r=3 -n="nbody-gnat-1"
poetry run fetch -- -r=3 -n="nbody-gnat-2"
poetry run fetch -- -r=3 -n="nbody-gnat-5"
poetry run fetch -- -r=3 -n="nbody-gnat-3"

poetry run fetch -- -r=3 -n="mandelbrot-rust-1"
poetry run fetch -- -r=3 -n="mandelbrot-rust-4" -d rust:rayon:1.7.0 rust:num-traits:0.2.15
poetry run fetch -- -r=3 -n="mandelbrot-gpp-1"
poetry run fetch -- -r=3 -n="mandelbrot-gpp-2"
poetry run fetch -- -r=3 -n="mandelbrot-gpp-3"
poetry run fetch -- -r=3 -n="mandelbrot-gcc-1"
poetry run fetch -- -r=3 -n="mandelbrot-gcc-2"
poetry run fetch -- -r=3 -n="mandelbrot-gcc-3"
poetry run fetch -- -r=3 -n="mandelbrot-gcc-4"
poetry run fetch -- -r=3 -n="mandelbrot-gnat-2"
poetry run fetch -- -r=3 -n="mandelbrot-gnat-3"

poetry run fetch -- -r=3 -n="fannkuchredux-rust-2"
poetry run fetch -- -r=3 -n="fannkuchredux-rust-4" -d rust:rayon:1.7.0
poetry run fetch -- -r=3 -n="fannkuchredux-rust-5" -d rust:rayon:1.7.0
poetry run fetch -- -r=3 -n="fannkuchredux-gcc-2"
poetry run fetch -- -r=3 -n="fannkuchredux-gcc-3"
poetry run fetch -- -r=3 -n="fannkuchredux-gcc-4"
poetry run fetch -- -r=3 -n="fannkuchredux-gnat-3"

poetry run fetch -- -r=3 -n="spectralnorm-rust-4" -d rust:rayon:1.7.0
poetry run fetch -- -r=3 -n="spectralnorm-rust-1"
poetry run fetch -- -r=3 -n="spectralnorm-rust-3"
poetry run fetch -- -r=3 -n="spectralnorm-rust-2"
poetry run fetch -- -r=3 -n="spectralnorm-gpp-1"
poetry run fetch -- -r=3 -n="spectralnorm-gpp-5"
poetry run fetch -- -r=3 -n="spectralnorm-gcc-1"
poetry run fetch -- -r=3 -n="spectralnorm-gcc-4"
poetry run fetch -- -r=3 -n="spectralnorm-gcc-3"
poetry run fetch -- -r=3 -n="spectralnorm-gnat-1"
poetry run fetch -- -r=3 -n="spectralnorm-gnat-3"
poetry run fetch -- -r=3 -n="spectralnorm-gnat-4"
