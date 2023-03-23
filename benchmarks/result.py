import time
from pydantic import BaseModel
from datetime import datetime

class RunResult(BaseModel):
    """The result of a single run with one input"""

    index: int           # position
    input: float = 0.0   # argument to program
    runtime: float = 0.0 # in ns

    # run timestamps
    start_time: int = 0
    stop_time: int = 0

    # ram and cpu load samples
    ram_samples: list[float] = []
    cpu_samples: list[float] = []

    average_cpu_load: float = 0.0 # in percent
    average_ram_load: float = 0.0 # in kb

    def start_timer(self):
        self.start_time = time.time_ns()

    def stop_timer(self):
        self.stop_time = time.time_ns()
        self.runtime = self.stop_time - self.start_time

    def runtime_s(self) -> float:
        return self.runtime_ms() / 1000000

    def runtime_ms(self) -> float:
        return self.runtime_ns() / 1000000

    def runtime_ns(self) -> float:
        return self.runtime

    def add_ram_sample(self, ram: float):
        self.ram_samples.append(ram)
        self.calculate_ram_load()

    def add_cpu_sample(self, cpu: float):
        self.cpu_samples.append(cpu)
        self.calculate_cpu_load()

    def calculate_cpu_load(self) -> float:
        self.average_cpu_load = sum(self.cpu_samples) / len(self.cpu_samples)
        return self.average_cpu_load

    def calculate_ram_load(self) -> float:
        self.average_ram_load = sum(self.ram_samples) / len(self.ram_samples)
        return self.average_ram_load

    def __repr__(self) -> str:
        return f"<RunResult runtime={self.runtime_ms()}>"
    
    def __str__(self) -> str:
        return self.__repr__()

class SeriesResult(BaseModel):
    """The collected results multiple runs with different inputs"""

    bench: str
    input: float = 0
    average_runtime: int = 0
    average_cpu_load: int = 0
    average_ram_load: int = 0
    run_results: list[RunResult] = []

    def append_result(self, result: RunResult):
        self.run_results.append(result)
        self.calculate()

    def calculate(self):
        self.calculate_runtime()
        self.calculate_cpu_load()
        self.calculate_ram_load()

    def calculate_runtime(self):
        # calculate average runtime
        total = sum(r.runtime_ns() for r in self.run_results)
        self.average_runtime = total / self.count()

    def calculate_cpu_load(self):
        # calculate average cpu_load
        total = sum(r.average_cpu_load for r in self.run_results)
        self.average_cpu_load = total / self.count()

    def calculate_ram_load(self):
        # calculate average ram_load
        total = sum(r.average_ram_load for r in self.run_results)
        self.average_ram_load = total / self.count()

    def count(self) -> int:
        return len(self.run_results)
        
    def __repr__(self) -> str:
        return f"<SeriesResult average={self.average}, count={self.count()}>"
    
    def __str__(self) -> str:
        return self.__repr__()
    
class SummaryResult(BaseModel):
    """The collected results of a benchmark run"""
    datetime: datetime

    # add other summary information here

    class Config:
        exclude = {"series"}

    def __init__(self, series: list[SeriesResult]):
        super().__init__(
            datetime=datetime.utcnow()

            # add other summary default information here

        )
        self.__build(series)

    def __build(self, series: list[SeriesResult]):
        
        # build summary information here
        
        pass