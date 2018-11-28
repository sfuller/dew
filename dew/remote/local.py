import time

import os
import shutil
import stat

from dew.dewfile import Dependency
from dew.remote import Remote


class LocalRemote(Remote):
    def __init__(self, dependency: Dependency) -> None:
        self.dependency = dependency

    def pull(self, dest_dir: str) -> None:
        if os.path.exists(dest_dir):
            if os.path.isdir(dest_dir):
                def remove_readonly(func, path, excinfo):
                    os.chmod(path, stat.S_IWRITE)
                    func(path)

                shutil.rmtree(dest_dir, onerror=remove_readonly)
            else:
                os.remove(dest_dir)
        shutil.copytree(self.dependency.url, dest_dir, copy_function=shutil.copy2)

    def get_version(self) -> str:
        # Return unix timestamp of most recent file modification time in source directory
        t = max(os.path.getmtime(root) for root, _, _ in os.walk(self.dependency.url))
        return str(int(t))
