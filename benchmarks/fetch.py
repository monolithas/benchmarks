# this script downloads a benchmarksgame report page and 
# installs it locally.

# NAME="nbody-gpp-0"

# URL=https://benchmarksgame-team.pages.debian.net/benchmarksgame/program/${NAME}.html
# PAGE=$(wget ${URL} -q -O -)

# echo $PAGE

import requests
import argparse
import bs4, os, shutil, glob
import shlex
import toml

from pathlib import Path

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

    # install a library at the system level

    # find the library

    # move it to the dependencies location

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

def options(text: str) -> tuple[list[str],list[str]]:
    start = "MAKE:"
    index = text.rfind(start)
    chunk = text[index + len(start):].strip()

    options = []
    options_ext = []

    position = 0

    for (i, part) in enumerate(shlex.split(chunk)):
        # skip the compiler path
        if i == 0:
            continue

        # we're collecting before the '-o' flag
        if position == 0:

            flag = None

            # get the preceding flag, if any
            if len(options) > 0:
                flag = options[-1]

            # collect flags
            if part.startswith('-'):
                options.append(part)

            # collect flag arguments
            elif flag and flag.startswith('-') and '=' not in flag:
                options.append(part)

            # if not a flag or arg, advance
            else:
                position = 1

        # we're skipping input and output files
        elif position == 1:
            if part.endswith('_run'):
                position = 2

        # we're collecting after the run file
        elif position == 2:

            # collect extended flags
            if part.startswith('-'):
                options_ext.append(part)

            # exit after getting extended flags
            else:
                break

        # should never happen
        else:
            break

    return (options, options_ext)

def download(name: str, bench: str, lang: str, count: str, local: str, dependencies: list[str]):
    url = f"https://benchmarksgame-team.pages.debian.net/benchmarksgame/program/{name}.html"

    # request the html for the page 
    page = requests.get(url)
    assert page.status_code == 200, "Failed to fetch html page"

    # parse the html as a BeautifulSoup object
    soup = bs4.BeautifulSoup(page.text, 'html.parser')

    # get the section that has the code in it
    sections = soup.article.findAll('section')

    code = sections[0].text
    opts, opts_ext = options(sections[1].text)

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
            "initial": opts,
            "extended": opts_ext
        },
        "dependencies": {
            "path": local,
            "names": dependencies
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
    

    # install the dependencies if necessary
    for dep in dependencies:
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

    os.chdir(path)

    # download the benchmark locally
    succeeded = False
    for _ in range(retry):
        try:
            download(name,bench,lang,count,deps_path,dependencies)
            succeeded = True
            break
        except:
            pass

    if not succeeded:
        raise RuntimeError(f"Failed to download html after {retry} tries") 