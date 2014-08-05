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
    if len(url_parts) < 5 or url_parts[3] not in ['tree', 'blob']:
        raise PathParseFail('URL parse failed: {}'.format(url_parts))
    return url_parts[1], url_parts[2], url_parts[4], '/'.join(url_parts[5:]), gh_path


def url_github_parse(url):
    """
    Returns: (user, repo, branch, file_path, gh_path)
    """

    url_parsed = urlparse(url)

    if url_parsed.scheme not in ['http', 'https']:
        url_parsed = urlparse('https://' + url_parsed.netloc +
            url_parsed.path)

    if not 'github' in url_parsed.netloc.lower():
        raise PathParseFail('URL parse failed: {}'.format(url))
    # strip everything except the path and
    # set the proto to https
    url_parsed = urlparse('https://github.com' + url_parsed.path)
    url_parts = url_parsed.path.split('/')
    if len(url_parts) < 5 or url_parts[3] not in ['tree', 'blob']:
        raise PathParseFail('URL parse failed: {}'.format(url_parts))
    return url_parts[1], url_parts[2], url_parts[4], '/'.join(url_parts[5:]), url_parsed.path
