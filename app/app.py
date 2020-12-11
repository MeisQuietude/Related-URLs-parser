from typing import Type, Union

from . import AppProvider
from .get import CmdGetProvider
from .load import CLILoadProvider
from .src.cli import args


def execute_command() -> Union[Type[AppProvider], None]:
    return {
        "get": CmdGetProvider,
        "load": CLILoadProvider,
    }.get(args.method.lower(), None)


def main():
    command = execute_command()()
    if command is None:
        return print(f"Unexpected method: `{args.method}`")
