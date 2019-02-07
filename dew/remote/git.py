from dew import git
from dew.dewfile import Dependency
from dew.remote import Remote


class GitRemote(Remote):

    def __init__(self, dependency: Dependency, dest_dir: str) -> None:
        self.dependency = dependency
        self.dest_dir = dest_dir

    def pull(self) -> None:
        repo, origin = git.get_repo(self.dependency.url, self.dest_dir)
        git.fetch(origin, self.dependency.head)
        git.checkout(repo, origin, self.dependency.head, self.dependency.ref)

    def get_latest_ref(self) -> str:
        repo, origin = git.get_repo(self.dependency.url, self.dest_dir)
        git.fetch(origin, self.dependency.head)
        return git.get_latest_ref(origin, self.dependency.head)

    def get_current_ref(self) -> str:
        repo, origin = git.get_repo(self.dependency.url, self.dest_dir)
        return repo.head.commit.hexsha

    def get_current_head(self) -> str:
        repo, origin = git.get_repo(self.dependency.url, self.dest_dir)
        return repo.active_branch.name

    def has_pending_changes(self) -> bool:
        repo, origin = git.get_repo(self.dependency.url, self.dest_dir)
        return repo.is_dirty(untracked_files=True)

    def get_source_dir(self) -> str:
        return self.dest_dir
