import argparse
import enum
from typing import Optional


class CommandType(enum.Enum):
    UPDATE = 'update'
    BOOTSTRAP = 'bootstrap'
    CLEAN = 'clean'
    UPGRADE = 'upgrade'
    WORKON = 'workon'
    FINISH = 'finish'
    BUILD = 'build'


class ArgumentData(object):
    def __init__(self) -> None:
        self.help = False
        self.command: Optional[CommandType] = None
        self.verbose = False
        self.version = False
        self.dewfile = 'dewfile.json'
        self.output_path = ''


def make_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--help', '-h', help='Show help information', action='store_true')
    parser.add_argument('command', type=CommandType,
                        help='Command to perform: ' + ', '.join(x.value for x in CommandType))
    parser.add_argument('--verbose', help='Be verbose', dest='verbose', action='store_true')
    parser.add_argument('--version', '-v', action='store_true', help='Output dew version')
    parser.add_argument('--output-path', help='Override the path used for storage of settings and prefixes.')
    parser.add_argument('--dewfile', metavar='DEWFILE_PATH', help='Override the path to the dewfile to use')
    return parser
