from watcher.models import WatcherUrl, WatcherUrlHistoryDay
import subprocess32
from subprocess32 import TimeoutExpired, STDOUT, CalledProcessError
from django.conf import settings
import tempfile
import boto
from path import path
from django.utils import timezone
from datetime import timedelta
from watcher.util import make_sure_path_exists

FRAME_RATE = 6  # frames/sec
VIDEO_LENGTH = 10
NUM_FRAMES = FRAME_RATE * VIDEO_LENGTH

SECONDS_IN_HOUR = 3600
MINUTES_IN_HOUR = 60
MINUTES_IN_DAY = 1440
MINUTES_IN_WEEK = 10080

look_back_seconds = 60 * 60 * 24
bucket_name = settings.BUCKET_NAME_DAY
s3_conn = boto.connect_s3()
bucket = s3_conn.create_bucket(
    bucket_name,
    location=boto.s3.connection.Location.DEFAULT)

now = timezone.now()
then = now - timedelta(seconds=look_back_seconds)
url = 'http://reddit.com'

watcher = WatcherUrl.objects.get(url=url, img=False)
capture_events = WatcherUrlHistoryDay.objects.filter(watcher_url=watcher, changed=True, created__range=[then, now]).order_by('created')

temp_dir = path(tempfile.mkdtemp())
make_sure_path_exists(temp_dir)

events = [((now - event.created).total_seconds(),
          (path(event.cap_path) / settings.CAP_HIGHLIGHT_FNAME,
           path(event.cap_path) / settings.LAST_CAP_HIGHLIGHT_FNAME)) for event in capture_events]
num_events = len(events) * 2
print("Num of events: {}".format(num_events))

sorted_events = sorted(events)
num = 1
for event in sorted_events:
    time = event[0]
    fpath = event[1]
    key_first = bucket.get_key(fpath[0])
    filename_first = temp_dir / "{:07d}-frame.png".format(num + 1)
    print("Writing {}: {}".format(time, filename_first))
    key_first.get_contents_to_filename(filename_first)

    key_second = bucket.get_key(fpath[1])
    filename_second = temp_dir / "{:07d}-frame.png".format(num)
    print("Writing {}: {}".format(time, filename_second))
    key_second.get_contents_to_filename(filename_second)
    num += 2

#cmd = "png2yuv -I p -f 6 -b 1 -n {} -j %07d-frame.png".format(num_events)
#print cmd
#print temp_dir
#with open(temp_dir / 'my.yuv', 'wb') as out:
#    subprocess32.check_call(
#        cmd,
#        stdout=out,
#        shell=True,
#        cwd=temp_dir,)
#
#
#cmd = "vpxenc --good --cpu-used=0 --auto-alt-ref=1 --lag-in-frames=16 --end-usage=vbr --passes=2 --threads=2 --target-bitrate=3000 -o my.webm my.yuv"
#print cmd
#print temp_dir
#subprocess32.check_call(
#    cmd,
#    shell=True,
#    cwd=temp_dir,)
