import os.path
import shutil
from typing import Callable


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
        f(self.get_builds_dir())
        f(self.get_downloads_dir())
        f(self.get_install_dir())

    def get_storage_dir(self):
        return self.join_storage_dir_path()

    def get_sources_dir(self):
        return self.join_storage_dir_path('sources')

    def get_builds_dir(self):
        return self.join_storage_dir_path('builds')

    def get_downloads_dir(self):
        return self.join_storage_dir_path('downloads')

    def get_install_dir(self):
        return self.join_storage_dir_path('prefix')

    def get_output_prefix_dir(self):
        return self.join_storage_dir_path('output-prefixes')

    def join_storage_dir_path(self, *args):
        return os.path.join(self.path, *args)
