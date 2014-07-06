from celery import Celery
import requests

from watcher.models import WatcherGit
from urlparse import urlparse

app = Celery('tasks', backend='redis://localhost', broker='redis://localhost')

@app.task
def check_url(url):
    # sanity check to see if
    # we get a 200 for the url
    response = requests.head(url)
    if not r.ok or r.headers.get('server') != 'GithHub.com':
        return 'errored'

