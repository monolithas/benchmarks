import os
import toml
import argparse

import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

from benchmarks.result import SummaryResult, SeriesResult
from benchmarks.utilities import setup_logger

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

    # convert all 'output/results/*' to SeriesResult objects
    log.debug("loading benchmark results")
    results = load_results('output/results/')

    # convert the 'output/summary.json' file to a SummaryResult object
    log.debug("loading benchmark summary")
    summary = SummaryResult.parse_file('output/summary.json')

    # sort the results for display
    collated = {}

    for result in results:
        bench = result.bench_name()
        complexity = result.bench_complexity()
        input = result.input
        lang  = result.language

        if bench not in collated:
            collated[bench] = {}

        if input not in collated[bench]:
            collated[bench][input] = {}

        if lang not in collated[bench][input]:
            collated[bench][input][lang] = result

    for benchmark, input_data in collated.items():

        # get labels for benchmark groupings
        inputs = tuple(str(k) for k in input_data.keys())

        results = {}
        maximum = 0.0

        for input, language_data in input_data.items():

            for language, series in language_data.items():
                if language not in results.keys():
                    results[language] = []

                # convert nanoseconds to milliseconds
                runtime = series.average_runtime / 1000000

                results[language].append(runtime)

                if runtime > maximum:
                    maximum = runtime

        x = np.arange(len(inputs))  # the label locations

        width = 0.1
        multiplier = 0

        fig, ax = plt.subplots(layout='constrained')

        for language, measurements in results.items():
            offset = width * multiplier
            rects = ax.bar(x + offset, measurements, width, label=language)
            ax.bar_label(rects, padding=3)
            multiplier += 1

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.legend(loc='upper left', ncols=4)
        ax.set_ylabel('Runtime (ns)')
        ax.set_xlabel('Input')
        ax.set_title(benchmark)

        ax.set_xticks(x + width, inputs)        
        ax.set_ylim(0, maximum * 1.01)

        plt.show()