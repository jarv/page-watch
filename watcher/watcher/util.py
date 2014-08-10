from urlparse import urlparse

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
