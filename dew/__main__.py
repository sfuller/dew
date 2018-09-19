import os
import json
import sys
import platform
from typing import Dict, Union

import dew
from dew.buildoptions import BuildOptionsCache, BuildOptions
from dew.dewfile import DewFileParser
from dew.exceptions import DewError
from dew.projectprocessor import ProjectProcessor
from dew.storage import StorageController
from dew.view import View


def main() -> int:
    parser = dew.make_argparser()
    args = parser.parse_args()

    view = View()
    view.show_verbose = True if args.v else False

    storage = StorageController(os.getcwd())
    storage.ensure_directories_exist()

    options_cache = BuildOptionsCache(storage)
    options = options_cache.get_options()
    if not options:
        options = BuildOptions()

    apply_argument_options(options, args)

    if args.defines is not None:
        for define in args.defines:
            options.options[define] = True

    options.options.update(get_builtin_options())

    options_cache.save_options(options)

    invalid_options = options.get_invalid_options()
    if len(invalid_options) > 0:
        view.error('The following options are either unset or set to invalid values:\n{0}\n'
                   'Please specify the correct values as arguments.'.format('\n'.join(invalid_options)))
        return 64

    dewfile_parser = DewFileParser()
    with open('dewfile.json') as file:
        dewfile_data = json.load(file)
    dewfile_parser.set_data(dewfile_data)
    dewfile = dewfile_parser.parse()

    project_processor = ProjectProcessor(storage, options, view, args.skip_download)
    project_processor.set_data(dewfile)

    try:
        project_processor.process()
    except DewError:
        view.error('Dew did not finish successfully :(')
        return 1

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
