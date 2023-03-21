from dataclasses import dataclass

@dataclass
class Result:
    runtime: int   # in ns
    cpuload: float # in percent
    memload: float  # in kb
    