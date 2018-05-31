from django.db import models
from model_utils import Choices
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class WatcherUrlNotifications(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email


class SuspiciousUrls(models.Model):
    url = models.CharField(max_length=500, unique=True)
    count = models.IntegerField(default=0)


class WatcherUrl(models.Model):
    STATUS = Choices('queued', 'processing', 'processed', 'errored', 'retrying')
    CAPTURE_TOOLS = Choices('phantomjs', 'wkhtmltoimage')
    INTERVALS = Choices('one', 'five', 'ten', 'fifteen', 'thirty', 'hour', 'day', 'week')
    status = models.CharField(max_length=32, default=STATUS.queued)
    user = models.CharField(max_length=255, default='', blank=True)
    interval = models.CharField(max_length=32, default=INTERVALS.day)
    url = models.CharField(max_length=500)
    img = models.BooleanField(default=True)
    last_error = models.TextField(default='', blank=True)
    last_output = models.TextField(default='', blank=True)
    error_count = models.IntegerField(default=0)
    timeout_count = models.IntegerField(default=0)
    save_output = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    notifications = models.ManyToManyField(WatcherUrlNotifications, blank=True)
    checks = models.IntegerField(default=0)
    changes = models.IntegerField(default=0)
    last_change = models.DateTimeField(null=True, blank=True)
    last_check = models.DateTimeField(null=True, blank=True)
    last_capture = models.URLField(blank=True)
    capture_tool = models.CharField(max_length=32, default=CAPTURE_TOOLS.wkhtmltoimage)
    screen_grab = models.BooleanField(default=False)
    checks_remaining = models.IntegerField(default=settings.MAX_CHECKS)
    unlimited = models.BooleanField(default=False)
    sponsor = models.TextField(default='', blank=True)

    class Meta:
        ordering = ('created',)
        unique_together = (("url", "img"),)

    def __str__(self):
        return self.url


class WatcherUrlBase(models.Model):
    STATUS = Choices('initialized', 'processing', 'processed', 'errored')
    status = models.CharField(max_length=32, default='')
    watcher_url = models.ForeignKey('WatcherUrl')
    bucket_name = models.CharField(max_length=100, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    md5 = models.CharField(max_length=32, default='')
    error = models.TextField(default='')
    changed = models.BooleanField(default=False)
    output = models.TextField(default='')
    cap_path = models.CharField(max_length=100, default='')


class WatcherUrlHistoryHour(WatcherUrlBase):
    pass


class WatcherUrlHistoryDay(WatcherUrlBase):
    pass


class WatcherUrlHistoryWeek(WatcherUrlBase):
    pass
