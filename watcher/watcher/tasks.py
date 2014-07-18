from celery import Celery
import requests

from watcher.models import WatcherGithub, WatcherGithubHistory
from urlparse import urlparse
from django.conf import settings
from os import path
from pprint import pprint
from djcelery.models import PeriodicTask, IntervalSchedule
app = Celery('tasks', backend='redis://localhost', broker='redis://localhost')

def _watcher_error(url, reason):
    watcher, created = WatcherGithub.objects.get_or_create(location=url)
    watcher.status = WatcherGithub.STATUS.errored
    watcher.last_error = reason
    watcher.save()

    task = PeriodicTask.objects.get(name=url)
    task.enabled = False
    task.save()


@app.task
def check_github_url(url):
    url_parsed = urlparse(url)

    watcher, created = WatcherGithub.objects.get_or_create(location=url_parsed.geturl())
    watcher.status = WatcherGithub.STATUS.processing
    watcher.save()

    # sanity check to see if
    # we get a 200 for the url

    response = requests.head(url_parsed.geturl())
    if not response.ok:
        reason = "bad response from url: {} reason: {}".format(
            url_parsed.geturl(),
            response.reason)
        _watcher_error(url, reason)
        return

    if not response.headers.get('server') != 'GitHub.com':
        reason = "URL {} is not a github url: {}".format(
            url_parsed.geturl(),
            response.headers.get('server'))
        _watcher_error(url, reason)
        return

    url_parts = url_parsed.path.split('/')
    if url_parts[3] not in ['tree', 'blob'] or len(url_parts) < 5:
        watcher.status = WatcherGithub.STATUS.errored
        watcher.last_error = 'url parse failed: {}'.format(url_parts)
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
    sha = r.json()[0]['sha']
    watcher_history, created = WatcherGithubHistory.objects.get_or_create(
        watchergithub=watcher,
        sha=sha,
    )
    watcher_history.save()
    watcher.status = WatcherGithub.STATUS.processed
    watcher.save()
