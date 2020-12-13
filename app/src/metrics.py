from logging import getLogger
from typing import Callable

from memory_profiler import memory_usage

Logger = getLogger(__name__)


def track_memory_decorator(function: Callable):
    """
    Log peak memory usage of function
    """

    def _wrapper(*args, **kwargs):
        result = max(
            memory_usage(proc=(function, args, kwargs), max_iterations=1)
        )
        Logger.info(f"Peak memory usage: {result} MiB")

    return _wrapper
