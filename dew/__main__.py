import os
import json
import sys
import platform
import shutil
from typing import Dict, Union

import dew.args
from dew.args import Arguments, CommandType
from dew.buildoptions import BuildOptionsCache, BuildOptions
from dew.depstate import DependencyStateController
from dew.dewfile import DewFileParser
from dew.exceptions import DewError
from dew.projectprocessor import ProjectProcessor
from dew.storage import StorageController
from dew.view import View


def main() -> int:
    parser = dew.args.make_argparser()
    args = Arguments()

    # noinspection PyTypeChecker
    parser.parse_args(namespace=args)

    view = View()
    view.show_verbose = True if args.verbose else False

    if args.version:
        print(f'dew {dew.VERSION_MAJOR}.{dew.VERSION_MINOR}.{dew.VERSION_PATCH}')
        return 0

    if args.command == CommandType.UPDATE:
        return update(args, view)
    if args.command == CommandType.BOOTSTRAP:
        return boostrap()
    if args.command == CommandType.CLEAN:
        return clean(args, view)

    view.error(f'Don\'t know how to handle command {args.command.value}! This is a bug.')
    return 1


def get_storage(args: Arguments) -> StorageController:
    if args.output_path:
        storage_path = args.output_path
    else:
        storage_path = os.path.join(os.getcwd(), '.dew')

    return StorageController(storage_path)


def update(args: Arguments, view: View) -> int:
    storage = get_storage(args)
    storage.ensure_directories_exist()

    options_cache = BuildOptionsCache(storage)
    options = options_cache.get_options()
    if not options:
        options = BuildOptions()

    apply_argument_options(options, args)

    if args.defines is not None:
        for define in args.defines:
            options.options[define] = True

    options.cmake_executable = args.cmake_executable

    options.options.update(get_builtin_options())

    options_cache.save_options(options)

    invalid_options = options.get_invalid_options()
    if len(invalid_options) > 0:
        view.error('The following options are either unset or set to invalid values:\n{0}\n'
                   'Please specify the correct values as arguments.'.format('\n'.join(invalid_options)))
        return 64

    dewfile_path = 'dewfile.json'
    if args.dewfile:
        dewfile_path = args.dewfile

    dewfile = dew.dewfile.parse_dewfile_with_local_overlay(dewfile_path)

    depstates = DependencyStateController(storage)
    depstates.load()

    project_processor = ProjectProcessor(storage, options, view, depstates)
    project_processor.set_data(dewfile)

    success = True

    try:
        project_processor.process()
    except DewError:
        view.error('Dew did not finish successfully :(')
        success = False

    if success and args.update_dummy_file:
        with open(args.update_dummy_file, 'a'):
            os.utime(args.update_dummy_file, None)

    depstates.save()

    return 0 if success else 1


def clean(args: Arguments, view: View) -> int:
    view.error('Not implemented yet!')
    return 1


def boostrap() -> int:
    src_path = os.path.join(__file__, '..', '..', 'cmake', 'dew.cmake')
    src_path = os.path.normpath(src_path)
    dest_path = os.path.join(os.getcwd(), 'dew.cmake')
    shutil.copy(src_path, dest_path)
    return 0


def apply_argument_options(options: BuildOptions, args) -> None:
    if args.cmake_generator:
        options.cmake_generator = args.cmake_generator


def get_builtin_options() -> Dict[str, Union[str, bool]]:
    options = {}
    if platform.system() == 'Darwin':
        if len(platform.mac_ver()[0]) > 0:
            options['DEW_PLATFORM_MACOS'] = True
    return options


sys.exit(main())
