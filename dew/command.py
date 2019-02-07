import argparse

from dew.args import ArgumentData
from dew.impl import CommandData
from dew.projectproperties import ProjectProperties


class Command(object):
    def get_argparser(self) -> argparse.ArgumentParser:
        pass

    def set_properties_from_args(self, args: ArgumentData, properties: ProjectProperties) -> None:
        pass

    def execute(self, args: ArgumentData, data: CommandData) -> int:
        pass

    def cleanup(self, args: ArgumentData, data: CommandData) -> None:
        pass
