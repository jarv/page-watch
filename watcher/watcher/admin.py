from django.contrib import admin
from watcher.models import WatcherGithub, WatcherGithubHistory, WatcherGithubNotifications

class WatcherGithubAdmin(admin.ModelAdmin):
    list_display = ('location', 'status', 'last_error', 'ratelimit_remaining' )

class WatcherGithubHistoryAdmin(admin.ModelAdmin):
    list_display = ('location', 'latest_sha', 'created')
    def location(self, obj):
        return obj.watchergithub.location

admin.site.register(WatcherGithub, WatcherGithubAdmin)
admin.site.register(WatcherGithubHistory, WatcherGithubHistoryAdmin)
admin.site.register(WatcherGithubNotifications)
