from typing import Type, Union

from .get import CmdGetProvider
from .load import CLILoadProvider
from .src.cli import args


def execute_command() -> Type[Union[str, CmdGetProvider, CLILoadProvider]]:
    return {
        "get": CmdGetProvider,
        "load": CLILoadProvider,
    }.get(args.method.lower(), str)


def main():
    command = execute_command()()
    if type(command) == str:
        return print(f"Unexpected method: `{args.method}`")
