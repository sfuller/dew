import dew.command
from dew.impl import CommandData


class ArgumentData(object):
    def __init__(self) -> None:
        pass


class Command(dew.command.Command):
    def execute(self, args: ArgumentData, data: CommandData) -> int:
        data.view.error('Not implemented yet')
        return 1
