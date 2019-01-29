import argparse
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
    data.view.error('Not implemented yet')
    return 1
