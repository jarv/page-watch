from django.contrib import admin
from watcher.models import WatcherGithub, WatcherGithubHistory

admin.site.register(WatcherGithub)
admin.site.register(WatcherGithubHistory)
