import os

from dew.dewfile import Dependency
from dew.remote import Remote


class LocalRemote(Remote):
    def __init__(self, dependency: Dependency, dest_dir: str) -> None:
        self.dependency = dependency

    def pull(self) -> None:
        pass

    def get_latest_ref(self) -> str:
        return str(int(self._get_latest_modtime()))

    def _get_latest_modtime(self) -> int:
        # Return unix timestamp of most recent file modification time in source directory
        return max(os.path.getmtime(root) for root, _, _ in os.walk(self.dependency.url))

    def get_current_ref(self) -> str:
        return self.get_latest_ref()

    def get_current_head(self) -> str:
        return self.dependency.head

    def has_pending_changes(self) -> bool:
        try:
            current_modtime = int(self.dependency.ref)
        except ValueError:
            return True
        return self._get_latest_modtime() > current_modtime

    def get_source_dir(self) -> str:
        return self.dependency.url
