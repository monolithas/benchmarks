import os
import toml
import argparse

from matplotlib import pyplot as plt
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
        bench = result.bench
        input = result.input
        lang  = result.language

        if bench not in collated:
            collated[bench] = {}

        if input not in collated[bench]:
            collated[bench][input] = {}

        if lang not in collated[bench][input]:
            collated[bench][input][lang] = result

