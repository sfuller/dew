from dew.dependencyprocessor import DependencyProcessor
from dew.dewfile import DewFile
from dew.storage import StorageController


class ProjectProcessor(object):

    def __init__(self, storage: StorageController):
        self.storage = storage
        self.dewfile = None

    def set_data(self, dewfile: DewFile):
        self.dewfile = dewfile

    def process(self):
        for dep in self.dewfile.dependencies:
            dep_processor = DependencyProcessor(self.storage)
            dep_processor.set_data(dep, self.dewfile)
            dep_processor.process()
