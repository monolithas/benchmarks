import os
import toml
import argparse

import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

from benchmarks.result import SummaryResult, SeriesResult
from benchmarks.utilities import setup_logger

BAR_WIDTH: float = 0.16
BAR_LABEL: str = '{:.2f}'

def load_result(path: Path | str) -> SeriesResult:
    path = Path(path)
    assert path.exists(), f"Path doesn't exist: {str(path)}"
    result = None

    try:
        result = SeriesResult.parse_file(path)
    except Exception as e:
        print(f"e: {e}, path={str(path)}")

    return result

def load_results(path: Path | str) -> list[SeriesResult]:
    results = []
    for root, _, files in os.walk(path):
        for name in files:
            file = Path(os.path.join(root, name))
            result = load_result(file)

            if result:
                results.append(result)
    return results

def create_runtime_analysis(path: Path, data: dict, config: dict):
    for benchmark, input_data in data.items():

        analysis_path = path / f'{benchmark}.runtime.png'

        input_data = list(input_data.items())
        input_data.sort(key=lambda v: v[0])

        # get labels for benchmark groupings
        inputs = tuple(str(k[0]) for k in input_data)

        results = {}
        limit = 0.0

        for _, language_data in input_data:

            for language, series in language_data.items():
                if language not in results.keys():
                    results[language] = []

                runtime = series.average_run_time_ms()
                maximum = series.maximum_run_time_ms()
                minimum = series.minimum_run_time_ms()

                results[language].append({
                    'runtime': runtime,
                    'minimum': runtime - minimum,
                    'maximum': maximum - runtime
                })

                if runtime > limit:
                    limit = runtime

                if maximum > limit:
                    limit = maximum

        x = np.arange(len(inputs))  # the label locations

        width = BAR_WIDTH
        count = 0

        _, ax = plt.subplots(layout='constrained')

        colors = {
            'rust': 'blue',
            'ada': 'green',
            'java': 'red',
            'c': 'lightgray',
            'cpp': 'gray'
        }

        # sort the measurements alphabetically
        keys = list(results.keys())
        keys.sort()
        results = {i: results[i] for i in keys}

        for language, measurements in results.items():
            offset = width * count
            
            # get measurements for display
            runtimes = [ v['runtime'] for v in measurements ]
            minimums = [ v['minimum'] for v in measurements ]
            maximums = [ v['maximum'] for v in measurements ]

            error = [minimums,maximums]

            # build a bar chart group
            group = ax.bar(
                x + offset, 
                runtimes, 
                width,
                yerr=error,
                label=language, 
                color=colors[language])

            # add value labels at the tops
            ax.bar_label(group, 
                padding=3, 
                fmt=BAR_LABEL)

            count += 1

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.legend(loc='upper left', ncols=count)
        ax.set_ylabel('Runtime (ms)')
        ax.set_xlabel('Input')
        ax.set_title(benchmark)

        ax.set_xticks(x + width, inputs)        
        ax.set_ylim(0, limit * 1.25)

        plt.gcf().set_size_inches(15, 5)
        plt.savefig(analysis_path, dpi=200)

def create_usage_analysis(path: Path, data: dict, config: dict):
    for benchmark, input_data in data.items():

        analysis_path = path / f'{benchmark}.cpu.png'

        input_data = list(input_data.items())
        input_data.sort(key=lambda v: v[0])

        # get labels for benchmark groupings
        inputs = tuple(str(k[0]) for k in input_data)

        results = {}
        limit = 0.0

        for _, language_data in input_data:

            for language, series in language_data.items():
                if language not in results.keys():
                    results[language] = []

                cputime = series.average_cpu_time_us()
                maximum = series.maximum_cpu_time_us()
                minimum = series.minimum_cpu_time_us()

                results[language].append({
                    'cputime': cputime,
                    'minimum': cputime - minimum,
                    'maximum': maximum - cputime
                })

                if cputime > limit:
                    limit = cputime

                if maximum > limit:
                    limit = maximum

        x = np.arange(len(inputs))  # the group locations

        width = BAR_WIDTH
        count = 0

        _, ax = plt.subplots()

        colors = {
            'rust': 'blue',
            'ada': 'green',
            'java': 'red',
            'c': 'lightgray',
            'cpp': 'gray'
        }

        # sort the measurements alphabetically
        keys = list(results.keys())
        keys.sort()
        results = {i: results[i] for i in keys}

        for language, measurements in results.items():
            offset = width * count
            
            # get measurements for display
            cputimes = [ v['cputime'] for v in measurements ]
            minimums = [ v['minimum'] for v in measurements ]
            maximums = [ v['maximum'] for v in measurements ]

            error = [minimums,maximums]

            # build a bar chart group
            group = ax.bar(
                x + offset, 
                cputimes, 
                width,
                yerr=error,
                label=language, 
                color=colors[language])

            # add value labels at the tops
            ax.bar_label(
                group, 
                padding=3,
                fmt=BAR_LABEL)

            count += 1

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.legend(loc='upper left', ncols=count)
        ax.set_ylabel('CPU Busy (us)')
        ax.set_xlabel('Input')
        ax.set_title(benchmark)

        ax.set_xticks(x + width, inputs)        
        ax.set_ylim(0, limit * 1.25)

        plt.gcf().set_size_inches(15, 5)
        plt.savefig(analysis_path, dpi=200)

def run():

    # define and parse command line arguments
    parser = argparse.ArgumentParser(
        prog='Display',
        description='Display results from benchmarks',
        epilog='Leave an issue on the repo if you have trouble')
    
    parser.add_argument('--config', 
        dest='config', 
        action='store',
        default='benchmarks.toml',
        help='Path to a toml config file')

    parser.add_argument('--logfile', 
        dest='logfile', 
        action='store',
        default=None,
        help='Path to a log file')
    
    parser.add_argument('--loglevel', 
        dest='loglevel', 
        action='store',
        default='warn',
        help='The level to log at')

    args = vars(parser.parse_args())

    # get the benchmark configuration file
    with open(args['config'], 'r') as f:
        config = toml.loads(f.read(), _dict=dict)

    assert config, "No configuration given"

    # get logging configuration parameters
    loglevel = args['loglevel'].upper()
    logfile = args['logfile']

    # initialize the logger for the application
    log = setup_logger(loglevel,logfile)

    # build paths for output and images
    root_path = Path('output')
    results_path = root_path / 'results'
    summary_path = root_path / 'summary.json'
    output_path = root_path / 'analysis'

    output_path.mkdir(exist_ok=True) 

    # load all results as SeriesResult objects
    log.debug("loading benchmark results")
    results = load_results(results_path)

    # load the summary as a SummaryResult object
    log.debug("loading benchmark summary")
    summary = SummaryResult.parse_file(summary_path)

    # sort the results for display
    collated = {}

    for result in results:
        bench = result.bench_name()
        input = result.input
        lang  = result.language

        if bench not in collated:
            collated[bench] = {}

        if input not in collated[bench]:
            collated[bench][input] = {}

        if lang not in collated[bench][input]:
            collated[bench][input][lang] = result

    create_runtime_analysis(output_path,collated,config)
    create_usage_analysis(output_path,collated,config)