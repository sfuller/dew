import argparse
from typing import List


class Arguments(object):
    def __init__(self) -> None:
        self.command = ''
        self.cmake_generator = ''
        self.verbose = False
        self.version = False
        self.skip_download = False
        self.defines: List[str] = []
        self.dewfile = ''
        self.output_path = ''
        self.update_dummy_file = ''
        self.cmake_executable = ''


def make_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', help='Be verbose', dest='verbose', action='store_true')
    parser.add_argument('--version', action='store_true')
    parser.add_argument('--skip-download', help='avoid downloading files', action='store_true')
    parser.add_argument('-D', action='append', dest='defines', help='Define the value of an option')

    subparsers = parser.add_subparsers(dest='command')

    bootstrap_parser = subparsers.add_parser('bootstrap')

    update_parser = subparsers.add_parser('update')
    update_parser.add_argument('--dewfile')
    update_parser.add_argument('--output-path')
    update_parser.add_argument('--dummy-file', dest='update_dummy_file')
    update_parser.add_argument('--cmake-generator')
    update_parser.add_argument('--cmake-executable')

    return parser
