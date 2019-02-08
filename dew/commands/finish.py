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
        parser.add_argument('name', metavar='DEPENDENCY', help='Name of the dependency to finish local work for')

    def execute(self, args: ArgumentData, data: CommandData) -> int:
        dewfile = data.project_parser.parse()

        target_dep: Dependency = None
        for dep in dewfile.dependencies:
            if dep.name == args.name:
                target_dep = dep

        if target_dep is None:
            data.view.error(f'Unknown dependency "{args.name}"')
            return 1

        if args.name not in dewfile.local_overrides:
            data.view.error(f'Local work on {args.name} has not been started.')
            return 1

        local_path = dewfile.local_overrides[args.name]

        processor = DependencyProcessor(data.storage, data.view, target_dep, dewfile, data.properties, source_dir=local_path)

        if processor.get_remote().has_pending_changes():
            data.view.error(f'Local {args.name} has pending changes. Please resolve.')
            return 1

        new_ref = processor.get_remote().get_current_ref()
        new_head = processor.get_remote().get_current_head()
        old_ref = target_dep.ref
        old_head = target_dep.head

        target_dep.ref = new_ref
        target_dep.head = new_head

        del dewfile.local_overrides[args.name]
        data.project_parser.save(dewfile)
        data.project_parser.save_local_work(dewfile)

        if new_ref != old_ref:
            data.view.info(
                f'Previous ref: {old_ref}\n'
                f'New ref:      {new_ref}'
            )
        if new_head != old_head:
            data.view.info(
                f'Previous head: {old_head}\n'
                f'New head:      {new_head}'
            )

        return 0
