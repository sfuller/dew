import os
import shutil

import dew.command
from dew.impl import CommandData


class ArgumentData(object):
    def __init__(self) -> None:
        pass


class Command(dew.command.Command):
    def execute(self, args: ArgumentData, data: CommandData) -> int:
        src_path = os.path.join(__file__, '..', '..', 'data', 'cmake', 'dew.cmake')
        src_path = os.path.normpath(src_path)
        dest_path = os.path.join(os.getcwd(), 'dew.cmake')
        shutil.copy(src_path, dest_path)
        return 0
