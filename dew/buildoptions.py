import json
import os.path
# from typing import List
from typing import Dict, Union

from dew.storage import StorageController


class BuildOptions(object):
    def __init__(self):
        self.cmake_generator = ''
        self.cmake_executable = ''
        self.options: Dict[str, Union[str, bool]] = {}

    def get_invalid_options(self):  # -> List[str]:
        invalid_options = []

        if not self.cmake_generator:
            invalid_options.append('cmake_generator')

        return invalid_options


class BuildOptionsCache(object):
    def __init__(self, storage: StorageController):
        self.storage = storage

    def get_options(self) -> BuildOptions or None:
        cache_path = self.get_cache_file_path()
        if os.path.isfile(cache_path):
            with open(cache_path) as f:
                data = json.load(f)
                return self.from_data(data)
        else:
            return None

    def save_options(self, options: BuildOptions) -> None:
        cache_path = self.get_cache_file_path()
        with open(cache_path, 'w') as f:
            json.dump(self.to_dict(options), f, indent=4)

    def from_data(self, data) -> BuildOptions:
        options = BuildOptions()
        options.cmake_generator = data['cmake_generator']
        return options

    def to_dict(self, options: BuildOptions) -> dict:
        data = dict()
        data['cmake_generator'] = options.cmake_generator
        return data

    def get_cache_file_path(self) -> str:
        return os.path.join(self.storage.get_storage_dir(), 'cache.json')
