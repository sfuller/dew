import sys

import argparse
import os
import platform
from typing import Dict, Union, Optional, List

import dew.args
from dew.args import ArgumentData, CommandType
from dew.projectproperties import ProjectPropertiesController
from dew.impl import CommandData
from dew.storage import StorageController
from dew.view import View
import dew.git
import dew.commands.update
import dew.commands.bootstrap
import dew.commands.clean
import dew.commands.upgrade


# TODO: Import these dynamically
command_module_map = {
    CommandType.UPDATE: dew.commands.update,
    CommandType.BOOTSTRAP: dew.commands.bootstrap,
    CommandType.CLEAN: dew.commands.clean,
    CommandType.UPGRADE: dew.commands.upgrade
}


def main() -> int:
    parser = dew.args.make_argparser()
    args = ArgumentData()

    # If there is a help flag defined, figure out what the positional argument is. Turns out argparse is kinda lame.
    argv: List[str] = sys.argv.copy()
    del argv[0]
    is_help = False
    positional: Optional[str] = None

    if '-h' in argv or '--help' in argv:
        is_help = True
        is_parsing_param = False
        for arg in argv:
            if is_parsing_param:
                continue
            if len(arg) > 0:
                if arg[0] == '-':
                    if len(arg) == 1 or arg[1] == '-':
                        is_parsing_param = True
                    continue

            positional = arg
            break

    if '--version' in argv:
        print(f'dew {dew.VERSION_MAJOR}.{dew.VERSION_MINOR}.{dew.VERSION_PATCH}')
        return 0

    view = View()

    if is_help:
        help(view, positional, parser)
        return 1

    # noinspection PyTypeChecker
    _, remaining_args = parser.parse_known_args(namespace=args)

    view.show_verbose = True if args.verbose else False

    # Default command
    if not args.command:
        args.command = CommandType.UPDATE

    command_module = command_module_map.get(args.command)

    if command_module is None:
        view.error(f'Don\'t know how to handle command {args.command.value}! This is a bug.')
        return 1

    command_args = command_module.ArgumentData()
    command_argparser = get_module_argparser(command_module)
    # noinspection PyTypeChecker
    command_argparser.parse_args(remaining_args, namespace=command_args)

    storage = get_storage(args)
    properties = get_properties(args, storage, command_args, command_module)
    command_data = CommandData(args, view, storage, properties)

    return command_module.execute(command_args, command_data)


def get_module_argparser(module) -> argparse.ArgumentParser:
    return module.get_argparser()


def help(view: View, command: Optional[str], parser: argparse.ArgumentParser) -> None:
    command_type = None
    if command is not None:
        for e in CommandType:
            if e.value == command:
                command_type = e
                break

        if command_type is None:
            view.error(f'{command} is not a command!')
            return

    if command_type is not None:
        command_module = command_module_map.get(command_type)
        command_parser = get_module_argparser(command_module)
        module_help(view, command, command_parser)
        return

    parser.print_help()
    view.info('\nSpecify a command with the help flag for help on a specific command.')


def module_help(view: View, name: str, parser: argparse.ArgumentParser) -> None:
    print(f'Help for command "{name}":')
    parser.print_help()


def get_storage(args: ArgumentData) -> StorageController:
    if args.output_path:
        storage_path = args.output_path
    else:
        storage_path = os.path.join(os.getcwd(), '.dew')

    storage = StorageController(storage_path)
    storage.ensure_directories_exist()
    return storage


def get_properties(args: ArgumentData, storage: StorageController, command_args, command_module) -> ProjectPropertiesController:
    controller = ProjectPropertiesController(storage)
    controller.load()
    properties = controller.get()

    if args.defines is not None:
        for define in args.defines:
            properties.options[define] = True

    properties.options.update(get_builtin_options())
    command_module.set_properties_from_args(command_args, properties)
    controller.set(properties)
    return controller


def get_builtin_options() -> Dict[str, Union[str, bool]]:
    options = {}
    if platform.system() == 'Darwin':
        if len(platform.mac_ver()[0]) > 0:
            options['DEW_PLATFORM_MACOS'] = True
    return options


def main_with_exit() -> None:
    exit(main())
