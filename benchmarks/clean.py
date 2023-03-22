import argparse
from benchmarks.utilities import *

def run():
    # define and parse command line arguments
    parser = argparse.ArgumentParser(
        prog='Clean',
        description='Clean various parts of the project',
        epilog='Leave an issue on the repo if you have trouble')

    parser.add_argument('-t','--targets', 
        dest='targets',
        nargs='+',
        help='Any of "programs", "dependencies", or "output"')
    
    # parse the command line arguments
    args = vars(parser.parse_args())
    targets = args['targets']

    # iterate targets and run clear functions
    for target in targets:
        {
            "programs": clear_programs,
            "dependencies": clear_dependencies,
            "output": clear_output
        }[target]()