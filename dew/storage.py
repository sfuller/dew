import os.path
import shutil
from typing import Callable
from enum import Enum

class BuildType(Enum):
    Debug = 0
    Release = 1
BUILD_TYPE_NAMES = {BuildType.Debug: 'debug', BuildType.Release: 'release'}

class StorageController(object):

    def __init__(self, path):
        self.path = path

    def ensure_directories_exist(self):
        self.walk_directories(lambda p: os.makedirs(p, exist_ok=True))

    def clean(self):
        self.walk_directories(lambda p: shutil.rmtree(p))

    def walk_directories(self, f: Callable[[str], None]):
        f(self.get_storage_dir())
        f(self.get_sources_dir())
        f(self.get_downloads_dir())
        for t in BuildType:
            f(self.get_builds_dir(t))
            f(self.get_install_dir(t))

    def get_storage_dir(self) -> str:
        return self.join_storage_dir_path()

    def get_sources_dir(self) -> str:
        return self.join_storage_dir_path('sources')

    def get_builds_dir(self, build_type: BuildType) -> str:
        return self.join_storage_dir_path(f'builds-{BUILD_TYPE_NAMES[build_type]}')

    def get_build_dir(self, label: str, build_type: BuildType) -> str:
        return os.path.join(self.get_builds_dir(build_type), label)

    def get_downloads_dir(self) -> str:
        return self.join_storage_dir_path('downloads')

    def get_install_dir(self, build_type: BuildType) -> str:
        return self.join_storage_dir_path(f'prefix-{BUILD_TYPE_NAMES[build_type]}')

    def get_output_prefix_dir(self, build_type: BuildType) -> str:
        return self.join_storage_dir_path(f'output-prefixes-{BUILD_TYPE_NAMES[build_type]}')

    def join_storage_dir_path(self, *args) -> str:
        return os.path.join(self.path, *args)
