import toml
import argparse
import json

from pathlib import Path
from datetime import datetime

from benchmarks.program import Program
from benchmarks.result import SeriesResult, SummaryResult
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

def save_results_individual(results: list[SeriesResult], path: Path):
    for result in results:
        # get the result as json
        data = result.json(indent=4)

        # build the output json path
        filepath = Path(path)
        filepath = filepath / result.bench
        key  = f"{filepath.suffix}.{result.input}.json"
        filepath = filepath.with_suffix(key)

        # write the json to the output file
        with open(filepath,'w') as f:
            f.write(data)

def save_results_collated(results: list[SeriesResult], path: Path):
    benchmarks = {}

    for result in results:
        complexity = result.complexity
        bench = result.bench_name() 
        input = result.input
        data = result.dict()

        if bench not in benchmarks:
            benchmarks[bench] = {}

        if input not in benchmarks[bench]:
            benchmarks[bench][input] = {}

        if complexity not in benchmarks[bench][input]:
            benchmarks[bench][input][complexity] = []

        benchmarks[bench][input][complexity].append(data)

    for bench, inputs in benchmarks.items():

        filepath = path / f"{bench}.json"

        data = json.dumps({
            'name': bench,
            'inputs': inputs
        },indent=4)

        # write the json to the output file
        with open(filepath,'w') as f:
            f.write(data)

def save_summary(result: list[SeriesResult], path: Path):
    # summarize the benchmarks
    summary = SummaryResult(datetime=datetime.utcnow())
    summary.build(result)

    # write the summary to the output file
    with open(path,'w') as f:
        f.write(summary.json(indent=4))

def run():
    config = None # benchmark configuration

    # define and parse command line arguments
    parser = argparse.ArgumentParser(
        prog='Bencher',
        description='Benchmark tool to compare various languages',
        epilog='Leave an issue on the repo if you have trouble')

    parser.add_argument('-c','--config', 
        dest='config', 
        action='store',
        default='benchmarks.toml',
        help='Path to a toml config file')
    
    parser.add_argument('-o','--output', 
        dest='output', 
        action='store',
        default='output',
        help='Path to an output file')
    
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

    # find all programs for the benchmark run
    programs = find_programs(config)

    # get benchmark settings for program runs
    general = config.get('general',{})
    values  = config.get('values',{})
    runs    = int(general.get('runs','1'))
    timeout = int(general.get('timeout','3600'))

    # build paths to the result directories
    output_path = Path(args['output'])
    result_path = output_path / 'results'
    summary_path = output_path / 'summary.json'

    # create directories if they don't exist
    output_path.mkdir(exist_ok=True)
    result_path.mkdir(exist_ok=True)

    results = []

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
                config,
                input,
                runs,
                timeout
            )

            if result:
                results.append(result)
            else:
                log.warn(f"No result for {program.name()} (input={input})")

    save_results_collated(results,result_path)
    save_summary(results,summary_path)