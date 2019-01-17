from dew.args import ArgumentData
from dew.projectproperties import ProjectPropertiesController
from dew.storage import StorageController
from dew.view import View


class CommandData(object):
    def __init__(self, args: ArgumentData, view: View, storage: StorageController,
                 properties: ProjectPropertiesController):
        self.args = args
        self.view = view
        self.storage = storage
        self.properties = properties
