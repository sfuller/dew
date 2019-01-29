import argparse
import enum
from typing import List, Optional


class CommandType(enum.Enum):
    UPDATE = 'update'
    BOOTSTRAP = 'bootstrap'
    CLEAN = 'clean'
    UPGRADE = 'upgrade'


class ArgumentData(object):
    def __init__(self) -> None:
        self.help = False
        self.command: Optional[CommandType] = None
        self.verbose = False
        self.version = False
        self.defines: List[str] = []
        self.dewfile = ''
        self.output_path = ''
        self.update_dummy_file = ''


def make_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--help', '-h', help='Show help information', action='store_true')
    parser.add_argument('command', type=CommandType, help='Command to perform: ' + ', '.join(x.value for x in CommandType))
    parser.add_argument('-v', help='Be verbose', dest='verbose', action='store_true')
    parser.add_argument('--version', action='store_true')
    parser.add_argument('-D', action='append', dest='defines', help='Define the value of an option')
    parser.add_argument('--output-path')
    parser.add_argument('--dewfile')
    parser.add_argument('--dummy-file', dest='update_dummy_file')

    return parser
