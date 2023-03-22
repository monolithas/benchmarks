# this script downloads a benchmarksgame report page and 
# installs it locally.

# NAME="nbody-gpp-0"

# URL=https://benchmarksgame-team.pages.debian.net/benchmarksgame/program/${NAME}.html
# PAGE=$(wget ${URL} -q -O -)

# echo $PAGE

import requests
import argparse
import bs4, os, shutil, glob

from pathlib import Path

def install_cargo(name: str, version: str | None):
    # delete everything in tmp
    shutil.rmtree('tmp')

    # create the output directory
    Path('data/dependencies/rust').mkdir(exist_ok=True)

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

    # src = "target/release/deps/*"
    # dst = "../data/dependencies/rust/"

    # # copy the built dependencies to output
    # for file in glob.glob(src):
    #     shutil.copy(file,dst)

    # os.chdir('..')

    # # recreate the tmp directory
    # shutil.rmtree('tmp')
    # os.mkdir('tmp')

def install_c(name: str, version: str | None):
    # delete everything in tmp
    shutil.rmtree('tmp')

    # create the output directory
    Path('data/dependencies/c').mkdir(exist_ok=True)

    # # create a temporary cargo project
    # os.system('cargo new tmp')
    # os.chdir('tmp')

    # # add the dependency to the project
    # if version:
    #     os.system(f'cargo add {name}@{version}')
    # else:
    #     os.system(f'cargo add {name}')

    # # build the project with the dependency
    # os.system(f'cargo build --release')

    # src = "target/release/deps/*"
    # dst = "../data/dependencies/rust/"

    # # copy the built dependencies to output
    # for file in glob.glob(src):
    #     shutil.copy(file,dst)

    # os.chdir('..')

    # # recreate the tmp directory
    # shutil.rmtree('tmp')
    # os.mkdir('tmp')

def install(kind: str, name: str, version: str | None):

    # get the requested installer
    installer = {
        'cargo':install_cargo
    }[kind]

    # call it with the given name and version
    installer(name,version)

def download(name: str):
    url = f"https://benchmarksgame-team.pages.debian.net/benchmarksgame/program/{name}.html"

    # request the html for the page 
    page = requests.get(url)
    assert page.status_code == 200, "Failed to fetch html page"

    # parse the html as a BeautifulSoup object
    soup = bs4.BeautifulSoup(page.text, 'html.parser')

    # get the section that has the code in it
    section = soup.article.section.pre
    code = section.text

    # create the appropriate name for the program
    parts = name.split('-')
    
    bench = parts[0]
    lang  = parts[1]
    count = parts[2]
    
    # translate the names
    if lang in ('gpp'):
        lang = 'cpp'

    if lang in ('gnat'):
        lang = 'ada'

    if lang in ('gcc','clang'):
        lang = 'c'

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
        help='Space delimited dependencies in the format "<type>:<name>:<version>"')
    
    # parse the command line arguments
    args = vars(parser.parse_args())

    # install the dependencies if necessary
    for dep in args['dependencies']:
        parts = dep.split(':')

        # split up the triplets
        kind = parts[0]
        name = parts[1]
        version = None

        # version number is optional
        if len(parts) > 2:
            version = parts[2]

        # install the dependency locally
        install(kind,name,version)

    # download the benchmark locally
    download(args['name'])