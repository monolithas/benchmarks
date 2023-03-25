import toml
import argparse

from pathlib import Path
from datetime import datetime

from benchmarks.program import Program
from benchmarks.result import SummaryResult
from benchmarks.utilities import setup_logger

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
            if item.is_file() and item.suffix != '.toml':
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

    # get benchmark settings for program runs
    general = config.get('general',{})
    values  = config.get('values',{})
    runs    = int(general.get('runs','1'))
    timeout = int(general.get('timeout','3600'))
    sample  = int(general.get('sample','0.2'))

    # build paths to the result directories
    output_path = Path('output/')
    result_path = output_path / 'results'

    # create directories if they don't exist
    output_path.mkdir(exist_ok=True)
    result_path.mkdir(exist_ok=True)

    series = []

    # for each program, build and run the benchmark
    for program in programs:

        # get input values, if any
        target = program.target()
        inputs = values.get(target,[])

        # build the program in the tmp directory
        program.build(config)

        # run the program for each of the inputs
        for input in inputs:
            
            # get the series results
            result = program.series(
                input,
                runs,
                timeout
            )

            if not result:
                log.warn(f"No result for {program.name()} (input={input})")
                continue

            # build the output json path and write
            data = result.json(indent=4)
            path = result_path / result.bench
            key  = f"{path.suffix}.{input}.json"
            path = path.with_suffix(key)

            with open(path,'w') as f:
                f.write(data)

            # save the series result for summarization
            series.append(result)

    # summarize the benchmarks
    summary = SummaryResult(datetime=datetime.utcnow())
    summary.build(series)

    summary_path = output_path / 'summary.json'

    # write the summary to the output directory
    with open(summary_path,'w') as f:
        f.write(summary.json(indent=4))