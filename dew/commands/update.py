import os
import argparse
from typing import List

import dew.args
from dew.depstate import DependencyStateController
from dew.dewfile import Dependency
from dew.exceptions import DewError, DewfileError
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


def get_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--C', dest='c_compiler_path', help='Path to the C compiler')
    parser.add_argument('--CXX', dest='cxx_compiler_path', help='Path to the CXX compiler')
    parser.add_argument('--prefix', dest='additional_prefix_paths', action='append')
    parser.add_argument('--cmake-generator')
    parser.add_argument('--cmake-executable')
    return parser


def set_properties_from_args(args: ArgumentData, properties: ProjectProperties) -> None:
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


def execute(args: ArgumentData, data: CommandData) -> int:
    dewfile_path = 'dewfile.json'
    if data.args.dewfile:
        dewfile_path = data.args.dewfile

    try:
        dewfile = dew.dewfile.parse_dewfile_with_local_overlay(dewfile_path)
    except DewfileError as e:
        data.view.dewfile_error(e)
        return 1

    depstates = DependencyStateController(data.storage)
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

    dewfile = project_processor.update_refs()
    dew.dewfile.save_refs(dewfile, dewfile_path)

    success = True

    try:
        project_processor.process()
    except DewError:
        data.view.error('Dew did not finish successfully :(')
        success = False

    dummy_file_path = data.args.update_dummy_file
    if success and dummy_file_path:
        with open(dummy_file_path, 'a'):
            os.utime(dummy_file_path, None)

    depstates.save()

    return 0 if success else 1
