from django.contrib import admin
from watcher.models import WatcherGithub, WatcherGithubHistory

class WatcherGithubAdmin(admin.ModelAdmin):
    list_display = ('location', 'status', 'last_error')

class WatcherGithubHistoryAdmin(admin.ModelAdmin):
    list_display = ('location', 'sha')
    def location(self, obj):
        return obj.watchergithub.location

admin.site.register(WatcherGithub, WatcherGithubAdmin)
admin.site.register(WatcherGithubHistory, WatcherGithubHistoryAdmin)
