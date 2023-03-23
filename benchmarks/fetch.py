import requests
import argparse
import bs4, os, shutil, glob
import shlex
import toml
import logging

from dataclasses import dataclass
from pathlib import Path
from benchmarks.utilities import read_list, write_list

log = logging.getLogger()

@dataclass
class OptionState:
    stage: int
    index: int
    options: list[str]
    extended: list[str]
    item: str | None
    dependencies: list[str]

    def active(self) -> list[str]:
        if self.stage > 0:
            return self.extended
        else:
            return self.options

    def previous(self) -> str | None:
        opts = self.active()
        if len(opts) > 0:
            return opts[-1]

    def advance(self):
        self.stage += 1

def install_rust(name: str, version: str | None, location: str):
    # delete everything in tmp
    shutil.rmtree('tmp')

    # create the output directory
    Path(location).mkdir(exist_ok=True)

    # create a temporary cargo project
    os.system('cargo new tmp')
    os.chdir('tmp')

    # add the dependency to the project
    if version:
        os.system(f'cargo add {name}@{version}')
    else:
        os.system(f'cargo add {name}')

    # build the project with the dependency
    os.system(f'cargo build --release')

    src = "target/release/deps/*.rlib"
    dst = f"../{location}"

    # copy the built dependencies to output
    for file in glob.glob(src):
        shutil.copy(file,dst)

    os.chdir('..')

    # recreate the tmp directory
    shutil.rmtree('tmp')
    os.mkdir('tmp')

def install_c(name: str, version: str | None, location: str):
    raise NotImplementedError("This function hasn't been implemented")

def install_cpp(name: str, version: str | None, location: str):
    raise NotImplementedError("This function hasn't been implemented")

def install_ada(name: str, version: str | None, location: str):
    raise NotImplementedError("This function hasn't been implemented")

def install(kind: str, name: str, version: str | None, location: str):

    # get the requested installer
    installer = {
        'rust':install_rust,
        'c':install_c,
        'cpp':install_cpp,
        'ada':install_ada
    }[kind]

    # call it with the given name and version
    installer(name,version,location)

def options_rust_param(state: OptionState) -> OptionState:
    # skip the compiler path
    if state.index == 0:
        return state

    # we're collecting before the output/input files
    if state.stage == 0:
        prev = state.previous()

        # check if the current item is an argument
        if prev and prev.startswith('-') and len(prev) == 2:

            # ignore linker flags and paths
            if prev == '-L':
                state.options.pop()
            else:
                state.options.append(state.item)

        # check if the current item is an extern
        elif prev == '--extern':
            state.options.pop()
            file = Path(state.item).name
            state.dependencies.append(file)

        # check if the current item is a flag
        elif state.item.startswith('-'):
            state.options.append(state.item)

        # advance to the next stage
        else:
            state.advance()
    
    # we're skipping the output/input files
    elif state.stage == 1:
        if state.item.endswith('_run'):
            state.advance()

    # we're collecting after the output/input files
    elif state.stage == 2:

        # collect extended flags
        if state.item.startswith('-'):
            state.extended.append(state.item)

        # signal completed
        else:
            state = None

    # signal completed
    else:
        state = None

    # we're finished
    return state

def options_cpp_param(state: OptionState) -> OptionState:
    # skip the compiler path
    if state.index == 0:
        return state

    # we're collecting before the output/input files
    if state.stage == 0:
        prev = state.previous()

        # check if the current item is an argument
        if prev and prev.startswith('-') and len(prev) == 2:

            # ignore linker flags and paths
            if prev == '-L':
                state.options.pop()
            else:
                state.options.append(state.item)

        # check if the current item is a flag
        elif state.item.startswith('-'):
            state.options.append(state.item)

        # advance to the next stage
        else:
            state.advance()
    
    # we're skipping the output/input files
    elif state.stage == 1:
        if state.item.endswith('_run'):
            state.advance()

    # we're collecting after the output/input files
    elif state.stage == 2:

        # collect extended flags
        if state.item.startswith('-'):
            state.extended.append(state.item)

        # signal completed
        else:
            state = None

    # signal completed
    else:
        state = None

    # we're finished
    return state

def options_c_param(state: OptionState) -> OptionState:
    return options_cpp_param(state)

def options_ada_param(state: OptionState) -> OptionState:
    # skip the compiler path
    if state.index == 0:
        return state

    # we're skipping everything before gnatmake
    if state.stage == 0:
        if 'gnatmake' in state.item:
            state.advance()

    # we're collecting before the output/input files
    elif state.stage == 1:
        prev = state.previous()
        
        # check if the current item is an argument
        if prev and prev.startswith('-') and len(prev) == 2:
            state.options.append(state.item)

        # check if the current item is a flag
        elif state.item.startswith('-'):

            # ignore the -f flag used for input file
            if state.item != '-f':
                state.options.append(state.item)

        # advance to the next stage
        else:
            state.advance()
    
    # we're skipping the output/input files
    elif state.stage == 2:
        if state.item.endswith('_run'):
            state.advance()

    # we're collecting after the output/input files
    elif state.stage == 3:

        # collect extended flags
        if state.item.startswith('-'):
            state.extended.append(state.item)

        # signal completed
        else:
            state = None

    # signal completed
    else:
        state = None

    # we're finished
    return state

def options(text: str, lang: str) -> OptionState:
    start = "MAKE:"
    index = text.rfind(start)
    chunk = text[index + len(start):].strip()

    # state machine used ofr parsing params
    state = OptionState(
        stage = 0,
        index = 0,
        options = [],
        extended = [],
        item = None,
        dependencies = []
    )

    # iterate through all params until finished
    for (i, item) in enumerate(shlex.split(chunk)):
        state.index = i
        state.item = item

        # parse a single param by language
        tmp = {
            "rust": options_rust_param,
            "c": options_c_param,
            "cpp": options_cpp_param,
            "ada": options_ada_param
        }[lang](state)

        # update and continue or exit
        if tmp != None:
            state = tmp
        else:
            break

    return state

def download(name: str, bench: str, lang: str, count: str, local: str, dependencies: list[str]):
    url = f"https://benchmarksgame-team.pages.debian.net/benchmarksgame/program/{name}.html"

    # request the html for the page 
    page = requests.get(url)
    assert page.status_code == 200, "Failed to fetch html page"

    # parse the html as a BeautifulSoup object
    soup = bs4.BeautifulSoup(page.text, 'html.parser')

    # get the section that has the code in it
    sections = soup.article.findAll('section')

    code = sections[0].pre.text
    result = options(sections[1].text,lang)

    # build the output file and path
    file = f"{bench}-{count}.{lang}"
    path = Path('programs') / bench

    # make the output directory if it doesn't exist
    path.mkdir(exist_ok=True)

    # add the file name to the path
    path /= file

    # write the source code to the given file
    with open(path,'w') as f:
        f.write(code)

    # build a configuration for the program
    config = toml.dumps({
        "options": {
            "initial": result.options,
            "extended": result.extended
        },
        "dependencies": {
            "path": str(local),
            "names": dependencies,
            "files": result.dependencies
        }
    })

    # build a configuration path
    path = path.with_suffix(path.suffix + '.toml')

    # write the config to the given file
    with open(path,'w') as f:
        f.write(config)

def parse(name: str) -> tuple[str,str,str]:
    # split the name into parts
    parts = name.split('-')
    
    # get each segment of the name
    bench = parts[0]
    lang  = parts[1]
    count = parts[2]
    
    # translate the language ids
    if lang in ('gpp'):
        lang = 'cpp'

    if lang in ('gnat'):
        lang = 'ada'

    if lang in ('gcc','clang'):
        lang = 'c'

    # return as a tuple
    return (bench,lang,count)

def run():
    # define and parse command line arguments
    parser = argparse.ArgumentParser(
        prog='Fetch',
        description='Download and add benchmarks locally from benchmarksgame',
        epilog='Leave an issue on the repo if you have trouble')

    parser.add_argument('-n','--name', 
        dest='name', 
        action='store',
        help='Name of the benchmark in the format "<target>-<lang>-<number>"')
    
    parser.add_argument('-d','--dependencies', 
        dest='dependencies', 
        nargs='+',
        default=[],
        help='Space delimited dependencies in the format "<language>:<name>:<version>"')
    
    parser.add_argument('-r','--retry', 
        dest='retry',
        action='store',
        default=1,
        help='Number of times to retry downloading the benchmark page')
    
    # parse the command line arguments
    args = vars(parser.parse_args())
    path = os.getcwd()

    dependencies = args['dependencies']
    retry = int(args['retry'])

    assert retry > 0, "Must have positive value for retry"

    # split and interprete the name
    name = args['name']
    bench, lang, count = parse(name)

    # create a deps directory if it doesn't exist
    deps_path = Path(f"data/dependencies/{lang}/")
    deps_path.mkdir(exist_ok=True)

    # create the bench directory if it doesn't exist
    bench_path = Path(f"programs/{bench}")
    bench_path.mkdir(exist_ok=True)

    # TODO: Store a list of downloaded dependencies somewhere so we don't download the same ones twice
    deps_list = read_list("output/dependencies.list")

    # install the dependencies if necessary
    for dep in dependencies:

        if dep in deps_list:
            continue

        parts = dep.split(':')

        # split up the triplets
        kind = parts[0]
        library = parts[1]
        version = None

        # version number is optional
        if len(parts) > 2:
            version = parts[2]

        # install the dependency locally
        install(kind,library,version,deps_path)

        deps_list.append(dep)

    write_list("output/dependencies.list",deps_list)
    os.chdir(path)

    # download the benchmark locally
    succeeded = False
    for _ in range(retry):
        try:
            log.info(f"downloading {name}")
            download(name,bench,lang,count,deps_path,dependencies)
            succeeded = True
            break
        except:
            log.warn(f"failed to download")
            pass

    # check that the download succeeded
    if not succeeded:
        raise RuntimeError(f"Download failed: '{name}' ({retry} tries)") 