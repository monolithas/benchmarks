from os.path import abspath, basename
from pathlib import Path
from benchmarks.result import RunResult, SeriesResult
from benchmarks.measure import measure
from benchmarks.utilities import parse_command

import shutil
import logging
import subprocess
import os
import toml
import copy

log = logging.getLogger()

DEFAULTS: dict = {
    "options": {
        "initial": [],
        "extended": []
    },
    "dependencies": {
        "path": None,
        "names": [],
        "files": []
    }
}

class Program:
    
    def __init__(self, path: Path):
        self.results = None
        self.original = Path(abspath(path))
        assert(self.original.exists())

        self.__stdout = None
        self.__stderr = None

    def __toml(self, config: dict) -> dict:
        opts, exts = self.__params(config)

        # get a path to the toml file 
        base = self.original
        path = base.with_suffix(base.suffix + '.toml')

        result = copy.deepcopy(DEFAULTS)

        # merge the default config with the loaded config
        if path.exists():
            result.update(toml.load(path))

        initial = result['options']['initial']
        extended = result['options']['extended']

        # combine the global options and extended options
        initial.append(opts)
        extended.append(exts)

        # remove duplicate options and update config
        result['options']['initial'] = initial
        result['options']['extended'] = extended

        # return the configuration
        return result

    def __tool(self, config: dict) -> str:
        lang = self.language()
        tool = config        \
            .get('tools',{}) \
            .get(lang,None)
        
        assert tool, f"No tool in config for language \"{lang}\""
        return tool
    
    def __params(self, config: dict) -> str:
        lang = self.language()

        # get regular options (build-time)
        options = config       \
            .get('options',{}) \
            .get(lang,'')
        
        # get extended options (link-time)
        extended = config       \
            .get('options',{}) \
            .get(f"{lang}_ext",'')
        
        return (options,extended)
    
    def __runfile(self) -> Path:
        name = ""
        if self.language() == 'java':
            name = f'{self.target()}.java'
        else:
            name = f'{self.name()}_run'
        return Path(name)

    def path(self) -> Path:
        return self.original

    def name(self) -> str:
        return basename(self.original)

    def language(self) -> str:
        return self.original.suffix.lstrip('.')

    def target(self) -> str:
        name = str(self.original.name)
        return name.split('-')[0]
    
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

        # get the build variables
        test = self.target()
        test_var = 'TEST'

        # get the build tool
        tool = self.__tool(config)
        tool_var = f"{lang.upper()}_TOOL"

        # get the build arguments
        cfg = self.__toml(config)
        opts_var = f"{lang.upper()}_OPTS"
        opts_ext = f"{opts_var}_EXT"

        # delete everything in tmp
        shutil.rmtree(temp)

        # create the tmp directory
        Path(temp).mkdir()

        # copy the input file to tmp
        shutil.copy(self.original,temp)
        shutil.copy(makefile,temp)

        # set the environment variables
        os.environ[tool_var] = tool
        os.environ[test_var] = test 
        os.environ[opts_var] = ' '.join(cfg['options']['initial'])
        os.environ[opts_ext] = ' '.join(cfg['options']['extended'])

        # change directory to tmp
        os.chdir(temp)

        # run make
        result = subprocess.run([
            'make',
            '--makefile',
            basename(makefile),
            runfile
        ], capture_output=True, text=True)

        self.__stdout = result.stdout
        self.__stderr = result.stderr

        os.chdir(working)

    def run(self, config: dict, input: int | float, index: int, timeout: int) -> RunResult:
        log.debug(f"Running program {self.name()}")
        result = RunResult(index=index,input=input)

        # get various paths and names for build
        working = os.getcwd()
        runfile = self.__runfile()
        temp = abspath('tmp')

        # change directories to tmp
        os.chdir(temp)

        # convert runfile path to an absolute path
        runfile = runfile.absolute()

        # if runfile is not found print build output
        if not runfile.exists():
            print(self.__stdout)
            print(self.__stderr)

        # verify that the run file exists
        assert runfile.exists(), f"File does not exist: {str(runfile)}"

        arguments = {
            'language': self.language(),
            'benchmark': self.target(),
            'binary': str(runfile),
            'input': str(input)
        }

        # get command if possible
        command = parse_command(config,arguments)

        # if the command wasn't found, assume simple command
        if not command:
            command = [str(runfile),str(input)]

        log.debug(f"Running: {command}")
        result = measure(index, command, input, timeout)

        os.chdir(working)
        return result
    
    def series(self, config: dict, input: int | float, count: int = 1, timeout: int = 3600) -> SeriesResult:
        series = SeriesResult(
            bench=self.name(),
            input=input,
            language=self.language())

        for i in range(count):
            series.append_result(self.run(config,input,i,timeout))

        return series
        