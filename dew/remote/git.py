from dew import git
from dew.dewfile import Dependency
from dew.remote import Remote


class GitRemote(Remote):

    def __init__(self, dependency: Dependency) -> None:
        self.dependency = dependency

    def pull(self, dest_dir: str) -> None:
        git.update_repo(self.dependency.url, dest_dir, self.dependency.ref)

    def get_version(self) -> str:
        return self.dependency.ref



