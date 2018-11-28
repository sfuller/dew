import argparse
import enum
from typing import List


class CommandType(enum.Enum):
    UPDATE = 'update'
    BOOTSTRAP = 'bootstrap'
    CLEAN = 'clean'


class Arguments(object):
    def __init__(self) -> None:
        self.command = CommandType.UPDATE
        self.cmake_generator = ''
        self.verbose = False
        self.version = False
        self.defines: List[str] = []
        self.dewfile = ''
        self.output_path = ''
        self.update_dummy_file = ''
        self.cmake_executable = ''


def make_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=CommandType, nargs='?', default=CommandType.UPDATE)
    parser.add_argument('-v', help='Be verbose', dest='verbose', action='store_true')
    parser.add_argument('--version', action='store_true')
    parser.add_argument('-D', action='append', dest='defines', help='Define the value of an option')
    parser.add_argument('--output-path')
    parser.add_argument('--dewfile')
    parser.add_argument('--dummy-file', dest='update_dummy_file')
    parser.add_argument('--cmake-generator')
    parser.add_argument('--cmake-executable')

    return parser
