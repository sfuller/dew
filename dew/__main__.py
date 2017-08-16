import os
import json

import dew
from dew.dewfile import DewFileParser
from dew.projectprocessor import ProjectProcessor
from dew.storage import StorageController


def main():
    parser = dew.make_argparser()
    args = parser.parse_args()

    storage = StorageController(os.getcwd())
    storage.ensure_directories_exist()

    dewfile_parser = DewFileParser()
    with open('dewfile.json') as file:
        dewfile_data = json.load(file)
    dewfile_parser.set_data(dewfile_data)
    dewfile = dewfile_parser.parse()

    project_processor = ProjectProcessor(storage)
    project_processor.set_data(dewfile)
    project_processor.process()

main()
