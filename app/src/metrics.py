from logging import getLogger
from time import perf_counter
from typing import Callable

from memory_profiler import memory_usage

Logger = getLogger(__name__)


def get_time_mem_metric(function: Callable):
    """
    Log peak memory and time usage of function
    """

    def _wrapper(*args, **kwargs):
        time_start = perf_counter()
        peak_memory_usage = max(
            memory_usage(proc=(function, args, kwargs), max_iterations=1)
        )
        time_end = perf_counter()
        execution_time = time_end - time_start

        Logger.info(f"Execution time {execution_time.__round__(2)} seconds")
        Logger.info(f"Peak memory usage: {peak_memory_usage} MiB")

    return _wrapper
