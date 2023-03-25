import os
import pickle
import time
import signal
import logging
import subprocess

from pathlib import Path
from threading import Thread
from benchmarks.result import RunResult

log = logging.getLogger()

class Timeout(Thread):

    def __init__(self, pid: int, timeout: int):
        Thread.__init__(self)
        self.setDaemon(1)
        self.pid = pid
        self.timeout = timeout
        self.timedout = False 

    def run(self):
        try: 
            self.wait()                           
        except:
            log.warn("Benchmark timed out")

    def wait(self):
        time.sleep(self.timeout)
        self.timedout = True
        os.kill(self.pid, signal.SIGKILL)

def measure(index: int, command: list[str], input: float, timeout: int) -> RunResult | None:
    r, w = os.pipe()
    pid = os.fork()

    # we are the parent process
    if pid:
        # not using write on this side
        os.close(w)
        result = None

        # read the result from the pipe
        with os.fdopen(r,'r') as f:
            result = RunResult.parse_raw(f.read())
        
        # wait for child process to exit
        os.waitpid(pid,0)
        return result

    # we are the child process
    else:

        # create a new run result object
        result = RunResult(index=index,input=input)

        try:
            timer = Timeout(pid,timeout)
            timer.start()

            log.debug("Starting benchmark")

            # start recording benchmark
            result.start_timer()
            result.start_cpu_check()

            # start the process
            process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)

            # stop recording benchmark
            result.stop_cpu_check()
            result.stop_timer()
            result.calculate()

            log.debug("Finished benchmark")

        except KeyboardInterrupt:
            os.kill(process.pid, signal.SIGKILL)

        except (OSError,ValueError):
            log.warn(f"Benchmark failed")
            result.failed = True

        finally:
            with os.fdopen(w,'w') as f:
                f.write(result.json())
            os._exit(0)