# Benchmarks

This project is based off of the [benchmarksgame](https://benchmarksgame-team.pages.debian.net/benchmarksgame/index.html) project and
is capable of downloading and formatting those programs for our own benchmarks. Unfortunately, the bencher tool included in the benchmarksgame
repo doesn't work with modern Python or on newer systems (Python 2.7, Ubuntu 18 etc.) so we decided to make our own.

## Examples

### Fetch an existing benchmark from benchmarksgame

`poetry run fetch -- -r=3 -n="nbody-rust-1"`

### Fetch an existing benchmark with dependencies

`poetry run fetch -- -r=3 -n="mandelbrot-rust-4" -d rust:rayon:1.7.0 rust:num-traits:0.2.15`

### Remove benchmark programs, dependencies and output files

`poetry run clean -- --targets programs dependencies output`

### Remove just benchmark programs

`poetry run clean -- --targets programs`

### Run existing benchmarks with log level and file

`poetry run bench -- --loglevel=debug --logfile=test.log`

### Run existing benchmarks without args

`poetry run bench`