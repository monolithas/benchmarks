from os.path import abspath, basename
from pathlib import Path
from benchmarks.result import Result

import shutil
import logging
import subprocess
import os
import psutil
import time

log = logging.getLogger()

class Program:
    
    def __init__(self, path: Path):
        self.results = None
        self.original = Path(abspath(path))
        assert(self.original.exists())

    def __tool(self, config: dict) -> str:
        lang = self.language()
        tool = config        \
            .get('tools',{}) \
            .get(lang,None)
        
        assert tool, f"No tool in config for language \"{lang}\""
        return tool
    
    def __params(self, config: dict) -> str:
        lang = self.language()
        tool = config          \
            .get('options',{}) \
            .get(lang,'')
        
        return tool
    
    def path(self) -> Path:
        return self.original

    def name(self) -> str:
        return basename(self.original)

    def language(self) -> str:
        return self.original.suffix.lstrip('.')

    def target(self) -> str:
        path = str(self.original.name)
        return path.split('-')[0]
    
    def build(self, config: dict):
        log.debug(f"Building program {self.name()}")
        
        # get various paths and names for build
        working = os.getcwd()
        runfile = f'{self.name()}_run'
        temp = abspath('tmp')
        lang = self.language()

        # get the makefile specified in config
        makefile = config      \
            .get('general',{}) \
            .get('makefile',None)

        assert makefile, f"No makefile specified in config"

        # get the build tool
        tool = self.__tool(config)
        tool_var = f"{lang.upper()}_TOOL"

        # get the build arguments
        opts = self.__params(config)
        opts_var = f"{lang.upper()}_OPTS"

        # delete everything in tmp
        shutil.rmtree(temp)

        # create the tmp directory
        Path(temp).mkdir()

        # copy the input file to tmp
        shutil.copy(self.original,temp)
        shutil.copy(makefile,temp)

        # set the environment variables
        os.environ[tool_var] = tool
        os.environ[opts_var] = opts

        # change directory to tmp
        os.chdir(temp)

        # run make
        subprocess.run([
            'make',
            '--makefile',
            basename(makefile),
            runfile
        ],check=True,
          stdout=subprocess.DEVNULL,
          stderr=subprocess.DEVNULL)

        os.chdir(working)

    def run(self, input: int | float):
        log.debug(f"Running program {self.name()}")
        result = Result(0,0,0)

        # get various paths and names for build
        working = os.getcwd()
        runfile = Path(f'{self.name()}_run')
        temp = abspath('tmp')

        # change directories to tmp
        os.chdir(temp)

        # convert runfile path to an absolute path
        runfile = runfile.absolute()

        # verify that the run file exists
        assert runfile.exists(), f"File does not exist: {str(runfile)}"

        start = time.time_ns()

        # start the process
        process = subprocess.Popen(
            [str(runfile),str(input)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)

        # calculate final run time of the program
        result.runtime = time.time_ns() - start

        os.chdir(working)
        return result