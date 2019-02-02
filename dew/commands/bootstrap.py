import os
import argparse
import shutil

from dew.impl import CommandData
from dew.projectproperties import ProjectProperties


class ArgumentData(object):
    def __init__(self) -> None:
        pass


def get_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    return parser


def set_properties_from_args(args: ArgumentData, properties: ProjectProperties) -> None:
    pass


def execute(args: ArgumentData, data: CommandData) -> int:
    src_path = os.path.join(__file__, '..', '..', '..', 'cmake', 'dew.cmake')
    src_path = os.path.normpath(src_path)
    dest_path = os.path.join(os.getcwd(), 'dew.cmake')
    shutil.copy(src_path, dest_path)
    return 0
