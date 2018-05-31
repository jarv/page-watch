import os
import errno
from urlparse import urlparse
from rest_framework.views import exception_handler
from django.conf import settings
import logging
from djcelery.models import PeriodicTask, IntervalSchedule
from django.utils import timezone
from watcher.models import SuspiciousUrls
from ago import human
import json
import re


logger = logging.getLogger(__name__)


def human_deltas(obj):

    deltas = dict()

    for attr in ('last_check', 'last_change', 'created', 'updated'):
        if hasattr(obj, attr) and getattr(obj, attr):
            deltas[attr] = human(timezone.now() - getattr(obj, attr))

    if hasattr(obj, 'checks_remaining'):
        if obj.unlimited:
            deltas['check_expiration'] = "never expire"
        elif obj.checks_remaining <= 0:
            deltas['check_expiration'] = "expire soon"
        else:
            if obj.interval == 'hour':
                deltas['check_expiration'] = human(timezone.timedelta(hours=-obj.checks_remaining), future_tense="expire in {}")
            elif obj.interval == 'day':
                deltas['check_expiration'] = human(timezone.timedelta(days=-obj.checks_remaining), future_tense="expire in {}")
            elif obj.interval == 'week':
                deltas['check_expiration'] = human(timezone.timedelta(days=-obj.checks_remaining), future_tense="expire in {}")

    return deltas


def custom_exception_handler(exc):
    response = exception_handler(exc)
    if response is not None:
        response.data['status'] = 'errored'
        if 'throttled' in str(exc):
            response.data['reason'] = 'Your making too many requests, try again later'
            response.status_code = 200
    return response


class RequestParseFail(Exception):
    pass


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def set_periodic_watcher_task(watcher, enabled=True):

    """
        Sets up a celery beat interval for the watcher
        at the configured interval. Will disable beat tasks
        at other intervals
    """
    ret = dict()

    logger.info("Setting periodic task for {} "
                "at interval {} enabled={} imgs={}".format(
                    watcher.url, watcher.interval,
                    enabled, watcher.img))

    if watcher.img:
        name = watcher.url
    else:
        name = watcher.url + "-noimg"

    every = settings.INTERVALS[watcher.interval]['every']
    period = settings.INTERVALS[watcher.interval]['period']

    interval, created = IntervalSchedule.objects.get_or_create(
        every=every,
        period=period,
    )
    if created:
        ret['interval_created'] = True
        interval.save()

    args = json.dumps([watcher.url, watcher.img])
    schedule, created = PeriodicTask.objects.get_or_create(name=name)
    save = False
    if created:
        ret['task_created'] = True
        schedule.interval = interval
        schedule.task = u'watcher.tasks.check_url_day'
        schedule.args = args
        schedule.enabled = enabled
        save = True

    if not created and schedule.interval != interval:
        ret['interval_changed'] = True
        schedule.interval = interval
        save = True

    if not created and schedule.task != u'watcher.tasks.check_url_day':
        ret['task_changed'] = True
        schedule.task = u'watcher.tasks.check_url_day'
        save = True

    if not created and schedule.enabled != enabled:
        ret['enabled_changed'] = True
        schedule.enabled = enabled
        save = True

    if not created and schedule.args != args:
        ret['arguments_changed'] = True
        schedule.args = args
        save = True

    if save:
        schedule.save()

    return ret


def _suspicious_url(url):
    s, created = SuspiciousUrls.objects.get_or_create(url=url)
    s.count += 1
    s.save()


def url_parse(url):
    """
    Returns: a sanitized version of a url
    """
    # remove all whitespace
    url = re.sub(r'\s+', '', url)
    if not settings.DEBUG:

        if len(url) > 500:
            logger.warning("URL submitted is too long: {url}".format(url=url))
            raise RequestParseFail("URL too long")

        if len(url) < 3:
            logger.warning("URL submitted is too short: {url}".format(url=url))
            raise RequestParseFail("Invalid URL")

        if '127.0.0.1' in url:
            logger.warning("URL submitted is suspicious: {url}".format(url=url))
            _suspicious_url(url)
            raise RequestParseFail("Invalid URL")

        if 'localhost' in url:
            logger.warning("URL submitted is suspicious: {url}".format(url=url))
            _suspicious_url(url)
            raise RequestParseFail("Invalid URL")

    try:
        parsed = urlparse(url)
    except Exception:
        logger.warning("Unable to parse URL: {url}".format(url=url))
        _suspicious_url(url)
        raise RequestParseFail("Invalid URL")

    if len(parsed.geturl().split('.')) < 2:
        logger.warning("URL to short: {parsed}".format(
            parsed=parsed))
        _suspicious_url(url)
        raise RequestParseFail("Invalid URL")

    if parsed.query:
        logger.warning("Query parmams submitted: {parsed}".format(parsed=parsed))
        raise RequestParseFail("No support for query parameters at this time")

    # m = re.search(p, parsed.geturl())
    # TODO BROKEN!
    # if m.group('port'):
    #    _suspicious_url(url)
    #    raise RequestParseFail("No support non-standard ports at this time")

    if not parsed.scheme:
        parsed = urlparse("http://" + parsed.geturl())
    if parsed.geturl():
        return parsed.geturl()
    else:
        logger.error("Something is not right, invalid URL: {parsed}".format(parsed))
        raise RequestParseFail("Invalid URL")
