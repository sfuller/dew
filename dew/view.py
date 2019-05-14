import os
import sys

import traceback

from dew.exceptions import DewfileError


class View(object):

    def __init__(self):
        self.show_verbose = False

    def info(self, message):
        print(message)

    def verbose(self, message):
        if self.show_verbose:
            print(message)

    def error(self, message):
        sys.stderr.write(message)
        sys.stderr.write(os.linesep)

    def dewfile_error(self, e: DewfileError) -> None:
        message = ''.join(traceback.format_exception(type(e.__cause__), e.__cause__, e.inner_tb))
        self.error(message)
        self.error(f'Failed to parse dewfile at path {e.file_path}')
        if e.reason:
            self.error(e.reason)
