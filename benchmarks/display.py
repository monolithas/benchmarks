import os
import toml
import argparse

import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

from benchmarks.result import SummaryResult, SeriesResult
from benchmarks.utilities import setup_logger

CHART_HEIGHT: int = 10 
CHART_WIDTH: int = 20

BAR_PAD_TOP: float = 0.25
BAR_WIDTH: float = 0.18
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

def save_chart(title: str, labels: list[str], path: Path, data: dict, ylabel: str | None = None, xlabel: str | None = None, sideways: bool = False):
    x = np.arange(len(labels))

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
    keys = list(data.keys())
    keys.sort()
    data = {i: data[i] for i in keys}

    for language, measurements in data.items():
        offset = width * count
        
        # get measurements for display
        values = [ v['value'] for v in measurements ]
        minimums = [ v['minimum'] for v in measurements ]
        maximums = [ v['maximum'] for v in measurements ]

        error = [minimums,maximums]

        group = None

        # build a bar chart group
        if sideways:
            group = ax.barh(
                x + offset, 
                values, 
                width,
                xerr=error,
                label=language, 
                color=colors[language])
        else:
            group = ax.bar(
                x + offset, 
                values, 
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

    if sideways:
        if ylabel: ax.set_xlabel(ylabel)
        if xlabel: ax.set_ylabel(xlabel)
    else:
        if ylabel: ax.set_ylabel(ylabel)
        if xlabel: ax.set_xlabel(xlabel)

    ax.set_title(title)

    if sideways:
        _, limit = ax.get_xlim()
        ax.set_xlim(0, limit * (1 + BAR_PAD_TOP))
        ax.set_yticks(x + width, labels)
        plt.gcf().set_size_inches(CHART_HEIGHT,CHART_WIDTH)
    else:
        _, limit = ax.get_ylim()
        ax.set_ylim(0, limit * (1 + BAR_PAD_TOP))
        ax.set_xticks(x + width, labels)
        plt.gcf().set_size_inches(CHART_WIDTH,CHART_HEIGHT)

    plt.savefig(path, dpi=200, bbox_inches='tight')

def create_runtime_analysis(path: Path, data: dict, config: dict):
    for benchmark, input_data in data.items():

        analysis_path = path / f'{benchmark}.runtime.png'

        input_data = list(input_data.items())
        input_data.sort(key=lambda v: v[0])

        # get labels for benchmark groupings
        inputs = tuple(str(k[0]) for k in input_data)

        results = {}

        for _, language_data in input_data:

            for language, series in language_data.items():
                if language not in results.keys():
                    results[language] = []

                value = series.average_run_time_ms()
                maximum = series.maximum_run_time_ms()
                minimum = series.minimum_run_time_ms()

                results[language].append({
                    'value': value,
                    'minimum': value - minimum,
                    'maximum': maximum - value
                })

        save_chart(
            title=benchmark,
            labels=inputs,
            path=analysis_path,
            data=results,
            ylabel='Runtime (ms)',
            xlabel='Input Values',
            sideways=True
        )

def create_usage_analysis(path: Path, data: dict, config: dict):
    for benchmark, input_data in data.items():

        analysis_path = path / f'{benchmark}.cpu.png'

        input_data = list(input_data.items())
        input_data.sort(key=lambda v: v[0])

        # get labels for benchmark groupings
        inputs = tuple(str(k[0]) for k in input_data)

        results = {}

        for _, language_data in input_data:

            for language, series in language_data.items():
                if language not in results.keys():
                    results[language] = []

                value = series.average_cpu_time_us()
                maximum = series.maximum_cpu_time_us()
                minimum = series.minimum_cpu_time_us()

                results[language].append({
                    'value': value,
                    'minimum': value - minimum,
                    'maximum': maximum - value
                })

        save_chart(
            title=benchmark,
            labels=inputs,
            path=analysis_path,
            data=results,
            ylabel='CPU Busy (us)',
            xlabel='Input Values'
        )

def run():

    # define and parse command line arguments
    parser = argparse.ArgumentParser(
        prog='Display',
        description='Display results from benchmarks',
        epilog='Leave an issue on the repo if you have trouble')
    
    parser.add_argument('-c','--config', 
        dest='config', 
        action='store',
        default='benchmarks.toml',
        help='Path to a toml config file')

    parser.add_argument('-f','--logfile', 
        dest='logfile', 
        action='store',
        default=None,
        help='Path to a log file')
    
    parser.add_argument('-l','--loglevel', 
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

    plt.rcParams.update({'font.size': 20})

    create_runtime_analysis(output_path,collated,config)
    create_usage_analysis(output_path,collated,config)