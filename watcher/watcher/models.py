from django.db import models
from model_utils import Choices

class WatcherGithub(models.Model):
    STATUS = Choices('initialized', 'processing', 'processed', 'errored')
    location = models.URLField(primary_key=True)
    status = models.CharField(max_length=32, choices=STATUS, default=STATUS.initialized)
    last_error = models.CharField(max_length=255)
    error_count = models.IntType()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created',)

class WatcherGithubHistory(models.Model):
    watchergithub = models.ForeignKey('WatcherGithub')
    sha = models.CharField(max_length=255, default=None)
    diff = models.URLField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
