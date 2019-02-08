import argparse
import dew.command
from dew.dependencyprocessor import DependencyProcessor
from dew.dewfile import Dependency
from dew.impl import CommandData


class ArgumentData(object):
    def __init__(self) -> None:
        self.name = ''


class Command(dew.command.Command):

    def setup_argparser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('name', metavar='DEPENDENCY', help='Name of the dependency to upgrade')

    def execute(self, args: ArgumentData, data: CommandData) -> int:
        dewfile = data.project_parser.parse()

        target_dep: Dependency = None
        for dep in dewfile.dependencies:
            if dep.name == args.name:
                target_dep = dep

        if target_dep is None:
            data.view.error(f'Unknown dependency "{args.name}"')
            return 1

        previous_ref = target_dep.ref

        processor = DependencyProcessor(data.storage, data.view, target_dep, dewfile, data.properties)
        target_dep.ref = processor.get_remote().get_latest_ref()
        data.project_parser.save(dewfile)

        if previous_ref != target_dep.ref:
            data.view.info(
                f'Dependency {args.name} upgraded.\n'
                f'Head:         {target_dep.head}\n'
                f'Previous ref: {previous_ref}\n'
                f'New ref:      {target_dep.ref}'
            )
        else:
            data.view.info(f'Dependency {args.name} is already at latest ref {previous_ref} for head {target_dep.head}')

        return 0
