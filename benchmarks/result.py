import os
import time
import psutil
import logging
from pydantic import BaseModel
from datetime import datetime

log = logging.getLogger()

class RunResult(BaseModel):
    """The result of a single run with one input"""

    # execution order
    index: int           # position

    # input value at execution
    input: float = 0.0

    # run timestamps
    run_time: float = 0.0 # in ns
    start_time: int = 0
    stop_time: int = 0

    # ram and cpu load samples
    ram_samples: list[float] = []
    cpu_samples: list[float] = []

    average_cpu_busy: float = 0.0

    # resource usage info
    user_cpu_time: float = 0.0  # user CPU time used
    sys_cpu_time: float = 0.0   # system CPU time used
    total_cpu_time: float = 0.0 # total CPU time used

    max_rss: int = 0           # maximum resident set size
    exit_code: int = 0         # the process exit code

    # utility flags
    failed: bool = False

    def start_cpu_check(self):
        psutil.cpu_percent(percpu=True)
        psutil.cpu_percent(percpu=True)

    def stop_cpu_check(self):
        s = psutil.cpu_percent(percpu=True) 
        self.cpu_samples = s

    def start_timer(self):
        self.start_time = time.time_ns()

    def stop_timer(self):
        self.stop_time = time.time_ns()
        self.run_time = self.stop_time - self.start_time

    def elapsed(self) -> float:
        return self.runt_ime_s()

    def run_time_s(self) -> float:
        return self.run_time_ms() / 1000000

    def run_time_ms(self) -> float:
        return self.run_time_ns() / 1000000

    def run_time_ns(self) -> float:
        return self.run_time
    
    def cpu_time_s(self) -> float:
        return self.cpu_time_ms() / 1000000

    def cpu_time_ms(self) -> float:
        return self.cpu_time_ns() / 1000000

    def cpu_time_ns(self) -> float:
        return self.total_cpu_time

    def calculate_cpu_load(self):
        run_time = self.run_time_s()
        scaled = [run_time*percent/100.0 for percent in self.cpu_samples]
        self.average_cpu_busy = sum(scaled)

    def calculate_mem_load(self):
        usage = os.wait3(0)
        self.user_cpu_time = usage[2][0] # user CPU time used
        self.sys_cpu_time = usage[2][1]  # system CPU time used
        self.max_rss = usage[2][2]       # maximum resident set size
        self.exit_code = usage[1]        # the process error code
        self.total_cpu_time = self.user_cpu_time + self.sys_cpu_time

    def calculate(self):
        self.calculate_cpu_load()
        self.calculate_mem_load()

    def __repr__(self) -> str:
        return f"<RunResult run_time={self.runtime_ms()}>"
    
    def __str__(self) -> str:
        return self.__repr__()

class SeriesResult(BaseModel):
    """The collected results multiple runs with different inputs"""

    bench: str
    language: str
    input: float = 0

    average_run_time: float = 0.0
    maximum_run_time: float = None
    minimum_run_time: float = None

    average_cpu_time: float = 0.0
    minimum_cpu_time: float = None
    maximum_cpu_time: float = None

    average_cpu_busy: int = 0
    average_ram_load: int = 0

    run_results: list[RunResult] = []

    def append_result(self, result: RunResult):
        self.run_results.append(result)
        self.calculate(result)

    def calculate(self, result: RunResult):
        self.calculate_run_time()
        self.calculate_cpu_usage()
        # self.calculate_ram_load()
        self.calculate_run_time_limits(result)
        self.calculate_cpu_time_limits(result)

    def calculate_run_time(self):
        # calculate average run_time
        total = sum(r.run_time_ns() for r in self.run_results)
        self.average_run_time = total / self.count()

    def calculate_cpu_usage(self):
        # calculate average cpu_load
        total = sum(r.cpu_time_ns() for r in self.run_results)
        self.average_cpu_time = total / self.count()

    def calculate_run_time_limits(self, result: RunResult):
        self.maximum_run_time = max(
            self.maximum_run_time or 0,
            result.run_time_ns())
        
        self.minimum_run_time = min(
            self.minimum_run_time or result.run_time_ns(),
            result.run_time_ns())
        
    def calculate_cpu_time_limits(self, result: RunResult):
        self.maximum_cpu_time = max(
            self.maximum_cpu_time or 0,
            result.cpu_time_ns())
        
        self.minimum_cpu_time = min(
            self.minimum_cpu_time or result.cpu_time_ns(),
            result.cpu_time_ns())

    def count(self) -> int:
        return len(self.run_results)
    
    def bench_name(self) -> str | None:
        return self.bench.split('-')[0]
    
    def bench_complexity(self) -> str | None:
        return self.bench.split('-')[1].split('.')[0]
        
    def average_run_time_ms(self) -> float:
        return self.average_run_time / 1000000
        
    def minimum_run_time_ms(self) -> float:
        return self.minimum_run_time / 1000000
    
    def maximum_run_time_ms(self) -> float:
        return self.maximum_run_time / 1000000
    
    def average_cpu_time_us(self) -> float:
        return self.average_cpu_time
        
    def minimum_cpu_time_us(self) -> float:
        return self.minimum_cpu_time
    
    def maximum_cpu_time_us(self) -> float:
        return self.maximum_cpu_time

    def __repr__(self) -> str:
        return f"<SeriesResult average={self.average_run_time_ms()}, count={self.count()}>"
    
    def __str__(self) -> str:
        return self.__repr__()
    
class SummaryResult(BaseModel):
    """The collected results of a benchmark run"""

    datetime: datetime

    # add other summary information here

    def build(self, series: list[SeriesResult]):
        
        # build summary information here
        
        pass