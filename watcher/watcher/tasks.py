from celery import Celery
import requests

from watcher.models import WatcherGithub, WatcherGithubHistory
from django.conf import settings
from djcelery.models import PeriodicTask, IntervalSchedule
from django.db import transaction
import json

app = Celery('tasks', backend='redis://localhost', broker='redis://localhost')

app.conf.update(
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_TIMEZONE='US/Eastern',
    CELERY_ENABLE_UTC=True,
)


@transaction.atomic
def _watcher_error(gh_path, reason, disable=False):
    watcher, created = WatcherGithub.objects.get_or_create(gh_path=gh_path)
    watcher.status = WatcherGithub.STATUS.errored
    watcher.last_error = reason
    watcher.error_count += 1
    if disable or watcher.error_count >= settings.MAX_ERRORS:
        try:
            task = PeriodicTask.objects.get(name=gh_path)
            task.enabled = False
            watcher.error_count = 0
            task.save()
        except PeriodicTask.DoesNotExist:
            pass
    print "Updating status"
    watcher.save()


@app.task
@transaction.atomic
def check_github_url(gh_path):

    watcher = WatcherGithub.objects.get(gh_path=gh_path)
    watcher.status = WatcherGithub.STATUS.processing
    watcher.save()

    api_url = "https://api.github.com/repos/{user}/{repo}/commits".format(
        user=watcher.user,
        repo=watcher.repo)

    params = dict(
        path=watcher.file_path,
        sha=watcher.branch
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
                r.status_code,
                r.reason)
            _watcher_error(gh_path, reason)
            return

        if len(r.json()) == 0:
            _watcher_error(gh_path, "No results returned for {}".format(gh_path))
            return

        commits = json.dumps(r.json(), indent=4, sort_keys=True)
        latest_sha = r.json()[0]['sha']
        watcher_previous = WatcherGithubHistory.objects.filter(
            watchergithub=watcher).order_by('-id').first()

        watcher_history, created = WatcherGithubHistory.objects.get_or_create(
            watchergithub=watcher,
            latest_sha=latest_sha,
        )

        if created:
            watcher_history.commits = commits
            watcher_history.save()

        if watcher_previous and watcher_previous.latest_sha != latest_sha:
            # Save the diff link since the last poll
            watcher_history.diff = "https://github.com/{user}/{repo}/compare/{previous}...{current}".format(
                previous=watcher_previous.latest_sha,
                current=latest_sha,
                user=watcher.user,
                repo=watcher.repo)

        watcher_history.save()
        watcher.ratelimit_remaining = r.headers['X-RateLimit-Remaining']
        watcher.ratelimit = r.headers['x-ratelimit-limit']
        watcher.status = WatcherGithub.STATUS.processed
        watcher.save()

        interval, created = IntervalSchedule.objects.get_or_create(
            every=settings.INTERVAL_EVERY, period=settings.INTERVAL_PERIOD
        )
        if created:
            interval.save()

        schedule, created = PeriodicTask.objects.get_or_create(
            name=watcher.gh_path,
            interval=interval,
            task=u'watcher.tasks.check_github_url',
            args=json.dumps([gh_path]),
        )

        if created:
            schedule.enabled = True
            schedule.save()

    except Exception as e:
        _watcher_error(gh_path, "Uncaught error during api fetch: " + str(e))
