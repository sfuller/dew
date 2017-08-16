import git.repo


def clone_repo(url, destination_dir, ref=None):
    kwargs = {
        'depth': 1
    }
    if ref is not None:
        kwargs['b'] = ref
    try:
        repo = git.repo.Repo(destination_dir)
    except (git.NoSuchPathError, git.InvalidGitRepositoryError):
        git.repo.Repo.clone_from(url, destination_dir, **kwargs)
        return
