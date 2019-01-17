import os

from dew.dewfile import Dependency
from dew.remote import Remote


class LocalRemote(Remote):
    def __init__(self, dependency: Dependency, source_dir: str, dest_dir: str) -> None:
        self.dependency = dependency
        self.dest_dir = dest_dir

    def pull(self) -> None:
        pass

    def get_latest_ref(self) -> str:
        # Return unix timestamp of most recent file modification time in source directory
        t = max(os.path.getmtime(root) for root, _, _ in os.walk(self.dependency.url))
        return str(int(t))

    def get_source_dir(self) -> str:
        return self.dependency.url
