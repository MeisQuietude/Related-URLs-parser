import argparse
import sys
from abc import ABC

parser = argparse.ArgumentParser()

parser.add_argument("method", type=str,
                    choices=["get", "load"],
                    help="'get' - show from db, 'load' - request and parse")
parser.add_argument("url", type=str)
parser.add_argument("-d", "--depth", type=int, default=1,
                    dest="depth", help="Limit depth to parse (default=1)")
parser.add_argument("-n", "--limit", type=int, default=0,
                    dest="limit", help="Limit to show urls (default=0)")
parser.add_argument("--allow-external-urls", default=False, action='store_true',
                    dest="allow_external_urls",
                    help="Allow links to other domains (default=False)")
parser.add_argument("--log-level",
                    choices=["debug", "info", "warning", "error"],
                    dest="log_level", default="info",
                    help="Level of logging info (default=INFO)")
parser.add_argument("--requests-batch-limit",
                    dest="bounded_semaphore", type=int, default=6,
                    help="Increase it when you can do more requests in one "
                         "batch or decrease in case you get HTTP-429 ("
                         "TooManyRequests) error (default=6)")


class ArgsI(ABC):
    method: str
    url: str
    depth: int
    limit: int
    allow_external_urls: bool
    log_level: str
    bounded_semaphore: int


# noinspection PyTypeChecker
args: ArgsI = parser.parse_args(sys.argv[1:])
