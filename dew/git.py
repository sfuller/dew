import posixpath

from typing import Optional, Tuple

import git.repo


def fetch(origin: git.Remote, refspec: Optional[str] = None) -> None:
    need_to_fetch_all = False

    try:
        origin.fetch(refspec=refspec)
    except git.GitCommandError as e:
        if 'unadvertised object' in e.stderr:
            # The ref might have been an unadvertised object (e.g. github does not advertise individual commits and
            # does not allow fetching an individual commit). If this is the case, we must fetch everything.
            need_to_fetch_all = True
        else:
            raise

    if need_to_fetch_all:
        origin.fetch()


def checkout(repo: git.Repo, origin: git.Remote, head_name: str, ref: str) -> None:
    if not repo.head.is_valid() or repo.head.commit.hexsha != ref:
        head = repo.create_head(path=head_name, commit=ref)

        tracking_ref = None
        for remote_ref in origin.refs:
            if remote_ref.remote_head == head_name:
                tracking_ref = remote_ref
                break

        head.set_tracking_branch(tracking_ref)
        head.checkout()

    for submodule in repo.submodules:
        # Hack around gitpython bug: https://github.com/gitpython-developers/GitPython/issues/730
        if submodule.url.startswith('..'):
            submodule_repo_name = submodule.url[3:]  # Strip off '../'
            repo_parent_url, _ = posixpath.split(origin.url)
            actual_url = posixpath.join(repo_parent_url, submodule_repo_name)
            with submodule.config_writer() as writer:
                writer.set('url', actual_url)

        print(f'Processing submodule {submodule.name}')
        submodule.update(init=True)


def get_repo(url: str, destination_dir: str) -> Tuple[git.Repo, git.Remote]:
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


def get_latest_ref(origin: git.Remote, head_name: str) -> str:
    ref: git.RemoteReference = None

    for head_ref in origin.refs:
        if head_ref.remote_head == head_name:
            ref = head_ref
            break

    if ref is None:
        raise ValueError('Could not find remote head!')

    return ref.commit.hexsha
