"""
Updates intervals for all watcher URLs
"""
from django.core.management.base import BaseCommand
from watcher.models import WatcherUrlHistoryDay
from watcher.tasks import get_screenshot
from watcher.models import WatcherUrl
from watcher.util import set_periodic_watcher_task
import logging


log_util = logging.getLogger('watcher.util')


class Command(BaseCommand):
    help = """

    Resets intervals for all watchers not
    in the error state

    """

    def handle(self, *args, **options):
        # squelch logging to console
        log_util.setLevel(logging.ERROR)
        print("Fetching watchers")
        watchers = WatcherUrl.objects.filter(status='processed')
        for watcher in watchers:
            if not WatcherUrlHistoryDay.objects.filter(watcher_url=watcher, status='processed').exists():
                print("No screenshot for interval, generating one for {}/{}".format(
                      watcher.url, watcher.img))
                get_screenshot.delay(url=watcher.url, img=watcher.img)
            else:
                if watcher.unlimited or watcher.checks_remaining > 0:
                    ret = set_periodic_watcher_task(watcher)
                else:
                    ret = set_periodic_watcher_task(watcher, False)
                if any(ret.values()):
                    print("URL changed: {url}/{img} {ret}".format(
                        url=watcher.url,
                        img=watcher.img,
                        ret=ret))
