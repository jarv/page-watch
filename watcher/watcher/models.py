from django.db import models

from model_utils import Choices

class WatcherGithub(models.Model):
    STATUS = Choices('initialized', 'processing', 'processed', 'errored')
    gh_path = models.CharField(max_length=2048, default='', db_index=True)
    user = models.CharField(max_length=255, default='')
    repo = models.CharField(max_length=255, default='')
    branch = models.CharField(max_length=255, default='')
    file_path = models.CharField(max_length=2048, default='')
    location = models.URLField()
    status = models.CharField(max_length=32, choices=STATUS, default=STATUS.initialized)
    last_error = models.TextField(default='')
    error_count = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    ratelimit_remaining = models.IntegerField(default=0)
    ratelimit = models.IntegerField(default=0)
    class Meta:
        ordering = ('created',)
    def get_absolute_url(self):
        return self.location

class WatcherGithubHistory(models.Model):
    watchergithub = models.ForeignKey('WatcherGithub')
    sha = models.CharField(max_length=255, default=None)
    diff = models.URLField()
    commit = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    commits = models.TextField(default='')

    def get_absolute_url(self):
        return self.watchergithub.location
    class Meta:
        unique_together = ('watchergithub', 'sha')
        ordering = ('created',)
