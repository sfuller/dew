import os
import argparse
from typing import List, Optional

import dew.command
from dew.depstate import DependencyStateController
from dew.impl import CommandData
from dew.projectprocessor import ProjectProcessor
from dew.projectproperties import ProjectProperties


class ArgumentData(object):
    def __init__(self) -> None:
        self.cmake_generator = ''
        self.cmake_executable = ''
        self.c_compiler_path = ''
        self.cxx_compiler_path = ''
        self.additional_prefix_paths: List[str] = []
        self.build_type = ''


class Command(dew.command.Command):
    def __init__(self) -> None:
        self.depstates: Optional[DependencyStateController] = None

    def setup_argparser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--CC', dest='c_compiler_path', help='Path to the C compiler')
        parser.add_argument('--CXX', dest='cxx_compiler_path', help='Path to the CXX compiler')
        parser.add_argument('--prefix', dest='additional_prefix_paths', action='append', metavar='PREFIX_PATH')
        parser.add_argument('--cmake-generator', help='The CMake generator to use for dependency projects')
        parser.add_argument('--cmake-executable', help='Path to the CMake executable')
        parser.add_argument('--build-type', help='"debug", "release", or "both"')

    def set_properties_from_args(self, args: ArgumentData, properties: ProjectProperties) -> None:
        if args.cmake_generator:
            properties.cmake_generator = args.cmake_generator
        if args.cmake_executable:
            properties.cmake_executable = args.cmake_executable
        if args.c_compiler_path:
            properties.c_compiler_path = args.c_compiler_path
        if args.cxx_compiler_path:
            properties.cxx_compiler_path = args.cxx_compiler_path
        if args.additional_prefix_paths:
            properties.prefixes = args.additional_prefix_paths
        if args.build_type:
            properties.build_type = args.build_type

    def execute(self, args: ArgumentData, data: CommandData) -> int:
        dewfile = data.project_parser.parse()
        depstates = DependencyStateController(data.storage)
        self.depstates = depstates
        depstates.load()

        is_dirty = data.properties.dirty
        if is_dirty:
            data.view.info('Dew project properties have changed. Clearing dependency state information.')
            depstates.clear()
            depstates.save()

        data.properties.save()
        properties = data.properties.get()

        project_processor = ProjectProcessor(data.storage, properties, data.view, depstates)
        project_processor.set_data(dewfile)

        dewfile, refs_have_changed = project_processor.update_refs()
        if refs_have_changed:
            data.project_parser.save_refs(dewfile)

        project_processor.process()
        return 0

    def cleanup(self, args: ArgumentData, data: CommandData) -> None:
        if self.depstates:
            self.depstates.save()
