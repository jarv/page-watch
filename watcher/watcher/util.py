

class PathParseFail(Exception):
    pass


def path_github_parse(gh_path):
    """
    Returns: (user, repo, branch, file_path, gh_path)
    """
    if not gh_path.startswith('/'):
        gh_path = "/{}".format(gh_path)

    url_parts = gh_path.split('/')
    if len(url_parts) < 5:
        raise PathParseFail('Error reading {} Submit a full github path.'.format(gh_path))

    if url_parts[3] not in ['tree', 'blob']:
        raise PathParseFail('Error reading {} Is this a valid github path?'.format(gh_path))
    return url_parts[1], url_parts[2], url_parts[4], '/'.join(url_parts[5:]), gh_path


def get_commit_info(commit):
    """
    Returns: (sha, login, login_url, name, avatar_url, commit_url, commit_msg)
    """

    # always able to get the sha
    sha = commit['sha']
    try:
        login = commit['committer']['login']
    except (KeyError, TypeError):
        login = None
    try:
        login_url = commit["committer"]["html_url"]
    except (KeyError, TypeError):
        login_url = None
    try:
        name = commit["commit"]["author"]["name"]
    except (KeyError, TypeError):
        name = None
    try:
        avatar_url = commit["committer"]["avatar_url"]
    except (KeyError, TypeError):
        avatar_url = "/imgs/github-anon.png"
    try:
        commit_url = commit["html_url"]
    except (KeyError, TypeError):
        commit_url = "https://github.com"
    try:
        commit_msg = commit["commit"]["message"]
    except (KeyError, TypeError):
        commit_msg = "No commit message"

    return sha, login.encode('utf-8'), login_url, name.encode('utf-8'), avatar_url, commit_url, commit_msg.encode('utf-8')
