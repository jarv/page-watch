from celery import Celery
import requests
from requests.exceptions import ConnectionError

from watcher.models import WatcherGithub, WatcherGithubHistory
from urlparse import urlparse
from django.conf import settings
from os import path
from pprint import pprint
from djcelery.models import PeriodicTask, IntervalSchedule
from django.db import transaction
import json

app = Celery('tasks', backend='redis://localhost', broker='redis://localhost')

@transaction.atomic
def _watcher_error(url, reason, disable=False):
    watcher, created = WatcherGithub.objects.get_or_create(location=url)
    watcher.status = WatcherGithub.STATUS.errored
    watcher.last_error = reason
    watcher.error_count += 1
    if disable or watcher.error_count >= settings.MAX_ERRORS:
        try:
            task = PeriodicTask.objects.get(name=url)
            task.enabled = False
            watcher.error_count = 0
            task.save()
        except PeriodicTask.DoesNotExist:
            pass
    watcher.save()

@app.task
def check_github_url(url):
    url_parsed = urlparse(url)

    watcher, created = WatcherGithub.objects.get_or_create(location=url_parsed.geturl())
    watcher.status = WatcherGithub.STATUS.processing
    watcher.save()

    # sanity check to see if
    # we get a 200 for the url
    try:
        response = requests.head(url_parsed.geturl())
        if not response.ok:
            reason = "bad response from url: {} status_code: {} reason: {}".format(
                url_parsed.geturl(),
                response.status_code,
                response.reason)
            _watcher_error(url, reason)
            return
    except Exception as e:
        print "Uncaught error during url pre-check - " + str(e)
        _watcher_error(url, str(e))
        raise

    if response.headers.get('server') != 'GitHub.com':
        reason = "URL {} is not a github url: ->{}<-".format(
            url_parsed.geturl(),
            response.headers.get('server'))
        _watcher_error(
            url,
            reason,
            disable=True)
        print "ERROR: " + reason
        return

    url_parts = url_parsed.path.split('/')
    if len(url_parts) < 5 or url_parts[3] not in ['tree', 'blob']:
        msg = 'URL parse failed: {}'.format(url_parts)
        _watcher_error(
            url,
            msg,
            disable=True)
        print "ERROR: " + msg
        return

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
    try:
        r = requests.get(
                api_url,
                headers={
                    "Authorization": "token " + settings.API_TOKEN
                },
                params=params
            )
        if r.status_code != 200:
            reason = "bad response from url: {} status_code: {} reason: {}".format(
                api_url,
                r.satus_code,
                r.reason)
            _watcher_error(url, reason)
            print "ERROR: " + reason
            return

        sha = r.json()[0]['sha']
        watcher_history, created = WatcherGithubHistory.objects.get_or_create(
            watchergithub=watcher,
            sha=sha,
        )
        watcher_history.save()
        watcher.status = WatcherGithub.STATUS.processed
        watcher.save()

        interval, created = IntervalSchedule.objects.get_or_create(
            every=settings.INTERVAL_EVERY, period=settings.INTERVAL_PERIOD
        )

        if created:
            interval.save()
        schedule, created = PeriodicTask.objects.get_or_create(
            name=url,
            interval=interval,
            task=u'watcher.tasks.check_github_url',
            args=json.dumps([url]),
        )
        schedule.enabled = True
        schedule.save()

    except Exception as e:
        print "Uncaught error during api fetch - " + str(e)
        _watcher_error(url, str(e))
        raise
