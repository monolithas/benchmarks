# Benchmarks

## Overview

This project is based off of the [benchmarksgame](https://benchmarksgame-team.pages.debian.net/benchmarksgame/index.html) project and
is capable of downloading and formatting those programs for our own benchmarks. Unfortunately, the bencher tool included in the benchmarksgame
repo doesn't work with modern Python or on newer systems (Python 2.7, Ubuntu 18 etc.) so we decided to make our own.

## Setup

In order to run the benchmarks, you'll probably need to be using an Ubuntu system- the tool isn't built to be particularly cross-platform. If you want to submit a PR to make it cross-platform, feel free and I'll review as quickly as I can. To set up the project on an Ubuntu system (only tested on Ubuntu 22.04):

1. Install Python 3.10.6 or greater
2. [Install Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)
3. Run `poetry update` in the project root directory
4. Install toolchains using the scripts in `scripts/toolchains/`
5. Done!

## Contributing

Feel free to fork and submit PRs against this project. The specific areas that need work are:

* Fetch currently only supports extracting arguments for C, C++, Rust, Ada, and Java benchmarks from the benchmarksgame website. This could be improved.
* Fetch currently only supports installing dependencies for Rust. This needs to be extended to support other languages.
* Display has a lot of hard-coded matplotlib code that could be more flexible and defined via CLI arguments instead of by changing the python.
* This project only runs on Ubuntu, and support needs to be added for Apple and Windows systems.
* No all metrics from benchmarksgame are supported- output binary size, for example. Those metrics could be implemented.

## Commands

### Fetch

**This command is only partially implemented!**

This tool can fetch benchmarks automatically from the benchmarksgame website and install them locally, but you should always manually verify that the benchmarks were imported correctly, and you may need to install dependencies or toolchains for the benchmarks that you import. To fetch a benchmark using the `fetch` command:

```bash
poetry run fetch -- -r=3 -n="mandelbrot-rust-4" -d rust:rayon:1.7.0 rust:num-traits:0.2.15
```

The **-r**/**--retry** flag determines the number of attempts that the fetch command will make to download the specified benchmark. The name of the benchmark is set with the **-n**/**--name** flag, and dependencies are added using the **-d**/**--dependencies** flag. Dependencies are given using a triplet `<language>:<name>:<version>` format in which the version is optional. 

Currently, only rust dependencies are supported, and only C, C++, Ada and Java benchmarks can be fetched. Adding fetch support for other languages should be relatively easy, however.

### Bench

The bench command excutes all benchmarks using the configuration declared in `benchmarks.toml`. All benchmarks are executed multiple times, and average as well as individual runtimes are output into the `output/results/` directory in JSON format. To run the benchmarks with the bench command:

```bash
poetry run bench -- -l=debug -f=test.log -o=output/ -c=benchmarks.toml
```

Bench takes `-l`/`--loglevel`, `-f`/`--logfile`, `-o`/`--output`, and `-c`/`--config` arguments that set the log level, set the log file, specify the output directory and specify the configuration file to use, respectively. The loglevel defaults to `info` logfile defaults to none, output is `output/` by default and config is `benchmarks.toml`.

### Display

The display command takes the output from the bench command and creates various charts in `output/analysis`. It's not particularly flexible at the moment, and if you want particular output, you're probably better off just modifying the `benchmarks/display.py` file. To create the charts from the output data, using the display command:

```bash
poetry run display -- -l=debug -f=benchmarks.log
```

This command takes the same loglevel and logfile arguments used by the bench command.

### Clean

To delete existing files, use the clean command:

```bash
poetry run clean -- --targets programs dependencies output
```

Clean takes a single argument that can take any combination of three space-delimited targets: `programs`, `dependencies`, or `output`. The "programs" target will delete all of the benchmarks under `programs/`, "dependencies" will delete the dependency files under `data/dependencies/language`, and "output" will delete benchmark charts and data from a bench run.
