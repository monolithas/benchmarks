import toml
import argparse
import logging

from pathlib import Path
from benchmarks.program import Program

def setup_logger(level: str, path: str = None):
    fmt = '%(asctime)s - %(levelname)s - %(module)s - %(message)s'
    formatter = logging.Formatter(fmt=fmt)

    # set the log level from command line
    logger = logging.getLogger()
    logger.setLevel(level.upper())

    # add a stream handler that logs to terminal
    term_handler = logging.StreamHandler()
    term_handler.setFormatter(formatter)
    logger.addHandler(term_handler)

    # if a path is given, add a file handler
    if path:
        file_handler = logging.FileHandler(path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def find_programs(config: dict) -> list[Program]:
    """
    Find all the programs specified in the config

    This function finds programs using the attributes
    listed under 'filters' ('include', 'exclude' etc.)
    """
    filters = config.get('filters',{})
    initial = filters.get('directories',[])
    include = filters.get('include',[])
    exclude = filters.get('exclude',[])
    ignore  = filters.get('ignore',[])
    
    result = []

    # get initial list of programs
    for path in initial:
        for item in Path(path).iterdir():
            if item.is_file():
                result.append(item)

    # include additional programs
    for path in include:
        path = Path(path)
        if path.exists():
            result.append(path)

    # exclude blacklisted programs
    for path in exclude:
        path = Path(path)
        result.remove(path)

    # exclude programs with given extensions
    tmp = []
    for path in result:
        if not path.suffix in ignore:
            tmp.append(path)
    result = tmp

    return [ Program(p) for p in result ]

def run():
    config = None # benchmark configuration

    # define and parse command line arguments
    parser = argparse.ArgumentParser(
        prog='Bencher',
        description='Benchmark tool to compare various languages',
        epilog='Leave an issue on the repo if you have trouble')

    parser.add_argument('--config', 
        dest='config', 
        action='store',
        default='benchmarks.toml',
        help='Path to a toml config file')
    
    parser.add_argument('--output', 
        dest='output', 
        action='store',
        default='results.xml',
        help='Path to an output file')
    
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

    # find all programs for the benchmark run
    programs = find_programs(config)
    results = []

    # get benchmark settings for program runs
    general = config.get('general',{})
    values  = config.get('values',{})
    runs    = int(general.get('runs','1'))
    timeout = int(general.get('timeout','3600'))
    sample  = int(general.get('sample','0.2'))


    # for each program, build and run the benchmark
    for program in programs:

        # get input values, if any
        target = program.target()
        inputs = values.get(target,[])

        # build the program in the tmp directory
        program.build(config)

        # run the program for each of the inputs
        for input in inputs:

            # run the program multiple times and average
            results = []
            for _ in range(runs):
                results.append(program.run(input))

            # display results
            times = [r.runtime/1000000 for r in results]
            log.debug(f" avg={sum(times)/runs} ms, all={times}")


        # results.append(program.result())

    # write the results to an output file
    for result in results:
        pass