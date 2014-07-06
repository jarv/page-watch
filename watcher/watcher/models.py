from django.db import models
from model_utils import Choices

class WatcherGit(models.Model):
    location = models.URLField()
    STATUS = Choices('initialized', 'processing', 'processed', 'errored')
    status = models.CharField(max_length=32, choices=STATUS, default=STATUS.initialized)
    preview_status = models.CharField(max_length=32, choices=STATUS, default=STATUS.initialized)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    current_sha = models.CharField(max_length=255)
    current_preview = models.URLField()

    class Meta:
        ordering = ('created',)

class WatcherGitHistory(models.Model):
    pass

