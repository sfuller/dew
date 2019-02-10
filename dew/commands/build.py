import argparse
import os

import dew.command
from dew.builder.cmake import CMakeBuilder
from dew.impl import CommandData
from dew.subprocesscaller import SubprocessCaller


class ArgumentData(object):
    def __init__(self) -> None:
        self.build_directory = ''


class Command(dew.command.Command):
    def setup_argparser(self, parser: argparse.ArgumentParser):
        parser.add_argument('build_directory', metavar='BUILD_DIRECTORY', help='Path to the build directory')

    def execute(self, args: ArgumentData, data: CommandData) -> int:
        caller = SubprocessCaller(data.view, redirect_output=False)

        builder = CMakeBuilder(
            buildfile_dir=os.getcwd(),
            build_dir=args.build_directory,
            install_dir=None,
            properties=data.properties.get(),
            caller=caller,
            view=data.view,
            additional_prefix_paths=(data.storage.get_install_dir(), )
        )

        builder.build()
        return 0
