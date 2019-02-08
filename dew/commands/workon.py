import os

import argparse
import shutil

import dew.command
import dew.args
from dew.dependencyprocessor import DependencyProcessor
from dew.dewfile import Dependency
from dew.impl import CommandData


class ArgumentData(object):
    def __init__(self) -> None:
        self.name = ''
        self.path = ''
        self.existing = False


class Command(dew.command.Command):

    def setup_argparser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('name', metavar='DEPENDENCY', help='Name of the dependency to work on locally')
        parser.add_argument('path', metavar='PATH',
                            help='Path to the directory where the dependency source will be put or is located')
        parser.add_argument('--existing', action='store_true',
                            help='Treat the given path as an existing source directory of the given dependency')

    def execute(self, args: ArgumentData, data: CommandData) -> int:
        dewfile = data.project_parser.parse()

        target_dep: Dependency = None
        for dep in dewfile.dependencies:
            if dep.name == args.name:
                target_dep = dep

        if target_dep is None:
            data.view.error(f'Unknown dependency "{args.name}"')
            return 1

        if args.name in dewfile.local_overrides:
            data.view.error(f'Local work on {args.name} has already been started.')
            return 1

        if not args.existing and os.path.exists(args.path) and len(os.listdir(args.path)) > 0:
            data.view.error('Target path is not empty. '
                            'Use the --existing flag to use this existing contents of this path.')
            return 1

        processor = DependencyProcessor(data.storage, data.view, target_dep, dewfile, data.properties)
        processor.get_remote().pull()

        if not args.existing:
            if os.path.exists(args.path):
                os.rmdir(args.path)
            shutil.copytree(processor.get_default_source_dir(), args.path)

        dewfile.local_overrides[args.name] = args.path
        data.project_parser.save_local_work(dewfile)
        return 0
