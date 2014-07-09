from celery import Celery
import requests

from watcher.models import WatcherGithub,
from urlparse import urlparse
from django.conf import settings
from os import path
from pprint import pprint
app = Celery('tasks', backend='redis://localhost', broker='redis://localhost')

@app.task
def add(x,y):
    return sum(x,y)

@app.task
def check_github_url(url):
    url_parsed = urlparse(url)

    watcher, created = WatcherGithub.objects.get_or_create(location=url_parsed.geturl())
    watcher.status = WatcherGithub.STATUS.processing
    watcher.save()

    # sanity check to see if
    # we get a 200 for the url

    response = requests.head(url_parsed.geturl())
    if not response.ok or response.headers.get('server') != 'GitHub.com':
        watcher.status = WatcherGithub.STATUS.errored
        watcher.save()
        return 'errored'

    url_parts = url_parsed.path.split('/')
    if url_parts[3] not in ['tree', 'blob'] or len(url_parts) < 5:
        watcher.status = WatcherGithub.STATUS.errored
        watcher.save()
        return 'errored'


    user = url_parts[1]
    repo = url_parts[2]
    branch = url_parts[4]
    path = '/'.join(url_parts[5:])

    api_url = "https://api.github.com/repos/{user}/{repo}/commits".format(
        user=user,
        repo=repo,
        path=path)
    params = dict(
        path=path,
        sha=branch
    )
    r = requests.get(
            api_url,
            headers={
                "Authorization": "token " + settings.API_TOKEN
            },
            params=params
        )
    watcher.current_sha = r.json()[0]['sha']
    watcher.status = WatcherGithub.STATUS.processed
    watcher.save()

