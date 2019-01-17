from dew import git
from dew.dewfile import Dependency
from dew.remote import Remote


class GitRemote(Remote):

    def __init__(self, dependency: Dependency, source_dir: str, dest_dir: str) -> None:
        self.dependency = dependency
        self.source_dir = source_dir
        self.dest_dir = dest_dir

    def pull(self) -> None:
        repo, origin = git.get_repo(self.dependency.url, self.dest_dir)
        git.fetch(origin, self.dependency.ref)
        git.checkout(repo, origin, self.dependency.ref)

    def get_latest_ref(self) -> str:
        reop, origin = git.get_repo(self.dependency.url, self.dest_dir)
        git.fetch(origin, self.dependency.head)
        return git.get_latest_ref(origin, self.dependency.head)

    def get_source_dir(self) -> str:
        return self.source_dir
