import sys

from typing import Optional, Tuple

import git.repo


def update_repo(url: str, destination_dir: str, ref: Optional[str]=None) -> None:
    repo, origin = setup_repo(url, destination_dir)
    fetch_and_checkout(repo, origin, ref)


def fetch_and_checkout(repo: git.Repo, origin: git.Remote, ref: Optional[str]=None) -> None:
    if not ref:
        ref = 'master'

    fetch_info = None
    need_to_fetch_all = False
    try:
        fetch_info = origin.fetch(refspec=ref)[0]
    except git.GitCommandError as e:
        if 'unadvertised object' in e.stderr:
            # The ref might have been an unadvertised object (e.g. github does not advertise individual commits and does
            # now allow fetching an individual commit). If this is the case, we must fetch everything.
            need_to_fetch_all = True
        else:
            raise

    if need_to_fetch_all:
        origin.fetch()
        head_commit = ref
    else:
        head_commit = fetch_info.ref.commit

    head = repo.create_head(path='dew-head', commit=head_commit)
    head.checkout(force=True)

    failed_fetching_submodules = False

    for submodule in repo.submodules:
        submodule.update(init=True)


def setup_repo(url: str, destination_dir: str) -> Tuple[git.Repo, git.Remote]:
    repo: git.Repo = None
    origin: git.Remote = None
    try:
        repo = git.repo.Repo(destination_dir)
    except (git.NoSuchPathError, git.InvalidGitRepositoryError):
        pass

    if repo is None:
        repo = git.repo.Repo.init(path=destination_dir, mkdir=True)

    for remote in repo.remotes:
        if remote.name == 'origin':
            origin = remote

    if origin is None:
        origin = repo.create_remote('origin', url)
    else:
        invalid_urls = set()
        for current_url in origin.urls:
            if current_url != url:
                invalid_urls.add(current_url)
        for invalid_url in invalid_urls:
            origin.set_url(url, invalid_url)

    return repo, origin
