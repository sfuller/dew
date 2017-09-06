import git.repo


def update_repo(url, destination_dir, ref=None):
    try:
        repo = git.repo.Repo(destination_dir)
    except (git.NoSuchPathError, git.InvalidGitRepositoryError):
        repo = clone_repo(url, destination_dir, ref)

    origin = repo.remotes[0]

    origin_url = next(origin.urls)
    if url != origin_url:
        origin.set_url(new_url=url, old_url=origin_url)

    fetch_and_checkout(repo, ref)


def fetch_and_checkout(repo, ref=None):
    if not ref:
        ref = 'master'
    repo.remotes[0].fetch()
    head = repo.create_head(ref)
    head.checkout(force=True)


def clone_repo(url, destination_dir, ref=None):
    kwargs = {
        'depth': 1
    }
    if ref:
        kwargs['b'] = ref
    return git.repo.Repo.clone_from(url, destination_dir, **kwargs)
