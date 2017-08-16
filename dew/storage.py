import os.path


class StorageController(object):

    def __init__(self, path):
        self.path = path

    def ensure_directories_exist(self):
        os.makedirs(self.get_storage_dir(), exist_ok=True)
        os.makedirs(self.get_sources_dir(), exist_ok=True)
        os.makedirs(self.get_builds_dir(), exist_ok=True)
        os.makedirs(self.get_downloads_dir(), exist_ok=True)
        os.makedirs(self.get_install_dir(), exist_ok=True)

    def get_storage_dir(self):
        return self.join_storage_dir_path()

    def get_sources_dir(self):
        return self.join_storage_dir_path('sources')

    def get_builds_dir(self):
        return self.join_storage_dir_path('builds')

    def get_downloads_dir(self):
        return self.join_storage_dir_path('downloads')

    def get_install_dir(self):
        return self.join_storage_dir_path('install')

    def get_storage_dir_name(self):
        return '.dew'

    def join_storage_dir_path(self, *args):
        return os.path.join(self.path, self.get_storage_dir_name(), *args)
