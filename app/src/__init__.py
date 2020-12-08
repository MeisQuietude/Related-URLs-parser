import logging

from app.src.cli import args

logging.basicConfig(
    format="[%(asctime)s] "
           "%(name)-8s "
           "%(levelname)-8s "
           "-  %(funcName)s "
           "- %(filename)s:%(lineno)d - %(message)s",
    datefmt="%y-%m-%dT%H:%M:%S.%s",
    level=logging.DEBUG
)

Logger = logging.getLogger()
Logger.setLevel(args.log_level.upper())
