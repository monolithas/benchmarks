import os, logging
from pathlib import Path

ROOT: Path = Path(__file__).parent.resolve()

DEFAULT_DEP_PATH:  Path = ROOT / '../data/dependencies/'
DEFAULT_PROG_PATH: Path = ROOT / '../programs/'
DEFAULT_OUT_PATH:  Path = ROOT / '../output/'

def setup_logger(level: str, path: str = None):
    """Configure the root logger used for the program"""
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

def clear(path: Path, keep: list[str] = []):
    for root, _, files in os.walk(path):
        for name in files:

            # skip delete of listed files
            if name in keep:
                continue

            # skip delete of hidden files
            if name.startswith('.'):
                continue    

            # delete the file
            os.unlink(os.path.join(root, name))

def clear_dependencies(path: Path = DEFAULT_DEP_PATH):
    clear(path)
            
def clear_programs(path: Path = DEFAULT_PROG_PATH):
    clear(path)

def clear_output(path: Path = DEFAULT_OUT_PATH):
    clear(path, keep=[ 'dependencies.list' ])

def read_list(path: Path | str) -> list[str]:
    path = Path(path)
    result = []

    # early return if the file doesn't exist
    if not path.exists():
        return result
    
    # read the file into a stripped list
    with open(path,'r') as f:
        for line in f.readlines():
            line = line.strip()
            if line:
                result.append(line)

    # remove duplicates and sort alphabetically
    result = sorted(list(set(result)))

    # return the list
    return result

def write_list(path: Path | str, data: list[str]):
    # sort list alphabetically
    data = sorted(data)

    path = Path(path)
    parent = path.parent

    # make sure the directory exists
    parent.mkdir(exist_ok=True)

    # write the list to the path
    with open(path,'w') as f:
        for item in data:
            f.write(f"{str(item)}\n")