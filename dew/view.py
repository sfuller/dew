import os
import sys


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
