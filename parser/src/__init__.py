import logging

from parser.src.cli import args
from parser.src.dbapi import session

debug_msg_format = (
    "[%(asctime)s] "
    "%(levelname)-8s "
    "-  %(funcName)s "
    "- %(filename)s:%(lineno)d - %(message)s"
)
info_msg_format = (
    "[%(asctime)s] "
    "%(levelname)-8s "
    "- %(message)s"
)

logging.basicConfig(
    format=(debug_msg_format if
            args.log_level.upper() == "DEBUG" else
            info_msg_format),
    datefmt="%y-%m-%dT%H:%M:%S.%s",
    level=logging.DEBUG
)

Logger = logging.getLogger()
Logger.setLevel(args.log_level.upper())
