from django.contrib import admin
from watcher.models import WatcherUrl, WatcherUrlNotifications, SuspiciousUrls
from watcher.models import WatcherUrlHistoryDay
from watcher.util import set_periodic_watcher_task
from django.utils import timezone
from ago import human
import logging

logger = logging.getLogger(__name__)


class WatcherUrlAdmin(admin.ModelAdmin):
    list_display = ('url', 'img', 'screen_grab', 'status', 'checks', 'changes', 'checks_remaining', 'error_count', 'unlimited', 'interval')

    def save_model(self, request, obj, form, change):
        if 'interval' in form.changed_data:
            logger.info("Interval has changed to {}".format(obj.interval))
            set_periodic_watcher_task(obj)
        super(WatcherUrlAdmin, self).save_model(request, obj, form, change)


class WatcherUrlHistoryAdmin(admin.ModelAdmin):
    list_display = ('url', 'img', 'status', 'changed', 'cap_path', 'updated', 'hupdated')

    def url(self, obj):
        return obj.watcher_url.url

    def img(self, obj):
        return obj.watcher_url.img

    def hcreated(self, obj):
        return human(timezone.now() - obj.created)

    def hupdated(self, obj):
        return human(timezone.now() - obj.updated)


class SuspiciousUrlsAdmin(admin.ModelAdmin):
    list_display = ('url', 'count')

admin.site.register(WatcherUrl, WatcherUrlAdmin)
admin.site.register(WatcherUrlHistoryDay, WatcherUrlHistoryAdmin)
admin.site.register(WatcherUrlNotifications)
admin.site.register(SuspiciousUrls, SuspiciousUrlsAdmin)
