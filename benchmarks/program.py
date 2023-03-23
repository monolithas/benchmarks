from os.path import abspath, basename
from pathlib import Path
from benchmarks.result import RunResult, SeriesResult

import shutil
import logging
import subprocess
import os
import toml
import time
import copy
import psutil

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

    def run(self, input: int | float, index: int) -> RunResult:
        log.debug(f"Running program {self.name()}")
        result = RunResult(index=index,input=input)

        # get various paths and names for build
        working = os.getcwd()
        runfile = Path(f'{self.name()}_run')
        temp = abspath('tmp')

        # change directories to tmp
        os.chdir(temp)

        # convert runfile path to an absolute path
        runfile = runfile.absolute()

        if not runfile.exists():
            print(self.__stdout)
            print(self.__stderr)

        # verify that the run file exists
        assert runfile.exists(), f"File does not exist: {str(runfile)}"

        # check the cpu usage
        psutil.cpu_percent(0,percpu=True) 

        from math import trunc

        # start the run timer
        result.start_timer()

        # start the process
        process = subprocess.Popen(
            [str(runfile),str(input)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)

        rusage = os.wait3(0)

        # stop the run timer
        result.stop_timer()

        # check the cpu usage
        elapsed = result.runtime_s()
        load = psutil.cpu_percent(0,percpu=True) 

        userSysTime = rusage[2][0] + rusage[2][1]    
        maxMem = rusage[2][2] 
        cpuLoad = ("% ".join([str(trunc(percent)) for percent in load]))+"%"
        elapsed = result.runtime_s()
        notIdle = sum([elapsed*percent/100.0 for percent in load])


        log.warn(f"     userSysTime: {userSysTime}")  
        log.warn(f"     maxMem: {maxMem}")  
        log.warn(f"     cpuLoad: {cpuLoad}")  
        log.warn(f"     elapsed: {elapsed}")  
        log.warn(f"     notIdle: {notIdle}")  

        os.chdir(working)
        return result
    
    def series(self, input: int | float, count: int = 1) -> SeriesResult:
        series = SeriesResult(bench=self.name(),input=input)

        for i in range(count):
            series.append_result(self.run(input,i))

        return series
        