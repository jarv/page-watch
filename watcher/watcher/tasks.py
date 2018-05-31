from celery import Celery

from watcher.models import WatcherUrl, WatcherUrlHistoryDay
from django.core.mail import send_mail
from urllib import quote_plus
from django.conf import settings
from djcelery.models import PeriodicTask
import subprocess32
import logging
import tempfile
from subprocess32 import TimeoutExpired, STDOUT, CalledProcessError
import boto
from boto.s3.key import Key
from path import path
from django.utils import timezone
from .util import make_sure_path_exists, set_periodic_watcher_task
from .notification import change_msg
from .image import crop_to_max, crop_to_match, create_thumbnail
from html2text import html2text
import os
from PIL import Image
from hashids import Hashids
import re

app = Celery('tasks')
app.config_from_object(settings)

hasher = Hashids(salt=settings.SECRET_KEY)
logger = logging.getLogger(__name__)


def _upload_images(watcher, watcher_history, key, temp_dir, cap_md5):

    cap_path = path("{w_hid}/{date}-{wh_hid}".format(
        w_hid=hasher.encrypt(watcher.id),
        date=timezone.now().strftime("%Y%m%d"),
        wh_hid=hasher.encrypt(watcher_history.id)))

    for fname in os.listdir(temp_dir):
        key.key = cap_path / fname
        key.cache_control = 'max-age=864000'
        key.metadata.update({
            'Cache-Control': 'max-age=864000'
        })
        key.set_contents_from_filename(temp_dir / fname)
        if fname.startswith(settings.SMALL_PREFIX):
            # make thumbnails public
            key.make_public()
    watcher_history.cap_path = cap_path
    watcher_history.bucket_name = settings.BUCKET_NAME_DAY
    watcher_history.md5 = cap_md5
    watcher_history.status = WatcherUrlHistoryDay.STATUS.processed
    watcher_history.save()


def _watcher_error(watcher, watcher_history=None, reason="", out="", disable=False):

    watcher.last_error = reason
    watcher.last_output += "\n\nOUTPUT FROM ERROR\n\n" + out
    watcher.error_count += 1
    watcher.status = WatcherUrl.STATUS.errored

    if watcher_history:
        watcher_history.status = WatcherUrl.STATUS.errored
        watcher_history.error = reason
        watcher_history.output += "\n\nOUTPUT FROM ERROR\n\n" + out
        watcher_history.save()

    if disable or watcher.error_count >= settings.MAX_ERRORS:
        try:
            set_periodic_watcher_task(watcher, False)
            watcher.error_count = 0
        except PeriodicTask.DoesNotExist:
            pass
    logger.info("Updating status")
    watcher.last_output += "\n\nOUTPUT FROM ERROR\n\n" + out
    watcher.save()
    return None


def _capture_page(watcher, temp_dir, url, out):

    try:
        capture_file = temp_dir / settings.CAP_FNAME

        if url.startswith("http"):
            capture_url = url
        else:
            capture_url = "http://" + url

        extra_capture_args = []
        logger.info("tool: {} img: {}".format(watcher.capture_tool, watcher.img))
        if watcher.capture_tool == 'phantomjs' and not watcher.img:
            extra_capture_args.append("--no-img")

        cmd = [settings.CAPTURE_TOOLS[watcher.capture_tool]] + \
            settings.CAPTURE_OPTS[watcher.capture_tool] + \
            [capture_url, capture_file] + \
            extra_capture_args
        logger.info("Capturing page `{}`".format(" ".join(cmd)))
        capture_out = subprocess32.check_output(
            cmd,
            stderr=STDOUT,
            timeout=settings.TIMEOUTS[watcher.capture_tool])

        out += capture_out

        # Error check for phantomjs
        if 'status: fail' in capture_out:
            raise Exception("PROCESS ERROR: output: {}".format(capture_out))

        cap_md5 = capture_file.read_md5().encode("hex")

    except CalledProcessError as e:
        raise Exception("PROCESS ERROR: {} ret:{} output: {}".format(
            str(e),
            e.returncode,
            e.output))
    except TimeoutExpired as e:
        watcher.timeout_count += 1
        watcher.save()
        raise Exception("TIMEOUT: {} - output: {}".format(
            str(e),
            e.output))

    crop_to_max(capture_file, url)
    create_thumbnail(capture_file)

    return cap_md5


@app.task
def get_screenshot(url, img=True):

    logger.info("grabbing screenshot for URL {}".format(url))
    out = ""
    watcher = WatcherUrl.objects.get(url=url, img=img)
    watcher_history = None
    watcher.status = WatcherUrl.STATUS.processing
    watcher.save()

    try:

        temp_dir = path(tempfile.mkdtemp())
        make_sure_path_exists(temp_dir)
        cap_md5 = _capture_page(watcher, temp_dir, url, out)

        s3_conn = boto.connect_s3()
        bucket = s3_conn.get_bucket(settings.BUCKET_NAME_DAY)
        key = Key(bucket)

        watcher_history = WatcherUrlHistoryDay.objects.create(
            watcher_url=watcher,
        )

        # upload images to bucket
        _upload_images(watcher, watcher_history, key, temp_dir, cap_md5)

        if watcher.save_output:
            watcher_history.output += out
        bucket = s3_conn.get_bucket(settings.BUCKET_NAME_DAY)
        key_small = bucket.get_key(
            path(watcher_history.cap_path) / settings.SMALL_PREFIX + settings.CAP_FNAME)
        cap_url_small = re.sub(r'\?x-amz-security-token.*', '', key_small.generate_url(expires_in=0, query_auth=False))
        watcher.last_capture = cap_url_small
        watcher.last_check = timezone.now()
        watcher.status = WatcherUrl.STATUS.processed
        watcher.last_output = out
        watcher.screen_grab = True
        watcher.save()

    except Exception as e:
        temp_dir.rmtree()
        _watcher_error(watcher, watcher_history, str(e), out)
        raise

    temp_dir.rmtree()
    set_periodic_watcher_task(watcher)


def _check_url(url, img):

    watcher_history = None
    watcher = WatcherUrl.objects.get(url=url, img=img)

    # output of commands
    out = ''

    watcher_history_last = WatcherUrlHistoryDay.objects.filter(
        watcher_url=watcher, status=WatcherUrl.STATUS.processed).order_by('-id').first()

    if not watcher_history_last:
        # no history, do nothing
        return

    s3_conn = boto.connect_s3()
    bucket = s3_conn.get_bucket(
        settings.BUCKET_NAME_DAY)
    key = Key(bucket)

    temp_dir = path(tempfile.mkdtemp())
    make_sure_path_exists(temp_dir)

    try:
        cap_md5 = _capture_page(watcher, temp_dir, url, out)
        watcher.checks += 1
        # Set the watcher status to processed
        # in case it was previously errored
        watcher.status = WatcherUrl.STATUS.processed
        watcher.last_check = timezone.now()
        if watcher.checks_remaining > 0:
            watcher.checks_remaining -= 1
        if watcher.checks_remaining <= 0 and not watcher.unlimited:
            set_periodic_watcher_task(watcher, False)
        watcher.error_count = 0
        watcher.save()

        # path to the bucket of the last cap
        bucket_last = s3_conn.get_bucket(settings.BUCKET_NAME_DAY)
        key_last = bucket_last.get_key(
            path(watcher_history_last.cap_path) /
            settings.CAP_FNAME)
        if not WatcherUrlHistoryDay.objects.filter(md5=cap_md5).first():
            # Fetch the last cap file to the current
            # temp dir
            key_last.get_contents_to_filename(
                temp_dir / settings.LAST_CAP_FNAME)

            crop_to_match(temp_dir / settings.CAP_FNAME,
                          temp_dir / settings.LAST_CAP_FNAME,
                          url=watcher.url)
            try:
                for env_var in ('CAP_FNAME', 'CAP_FNAME_RESIZED',
                                'CAP_HIGHLIGHT_FNAME', 'LAST_CAP_FNAME',
                                'LAST_CAP_FNAME_RESIZED', 'LAST_CAP_HIGHLIGHT_FNAME',
                                'MASK_FNAME', 'MASK_BLUR_FNAME',
                                'MASK_BLUR_MONOCHROME_FNAME'):
                    os.environ[env_var] = getattr(settings, env_var)

                out += "\n\nCOMPARE_SCRIPT OUT\n\n"
                out += subprocess32.check_output(
                    [settings.COMPARE_SCRIPT],
                    stderr=STDOUT,
                    timeout=settings.COMPARE_TIMEOUT, cwd=temp_dir)

            except CalledProcessError as e:
                raise Exception(
                    "PROCESS ERROR: {} ret:{} output: {}".format(
                        str(e),
                        e.returncode,
                        e.output))
            except TimeoutExpired as e:
                raise Exception(
                    "TIMEOUT: {} - output: {}".format(str(e), e.output))

            # check to see if there were any meaningful differences
            id_out = subprocess32.check_output(
                [settings.IDENTIFY_BIN, '-format', '%k',
                 temp_dir / settings.MASK_BLUR_MONOCHROME_FNAME, ],)
            out += "\n\nIDENTIFY_BIN OUT\n\n" + id_out
            if id_out.strip() == '2':
                # Create thumbnails
                for fname in os.listdir(temp_dir):
                    with Image.open(temp_dir / fname) as im:
                        im.thumbnail((settings.SMALL_WIDTH, settings.SMALL_HEIGHT), Image.ANTIALIAS)
                        im.save(temp_dir / settings.SMALL_PREFIX + fname)

                watcher_history = WatcherUrlHistoryDay.objects.create(
                    watcher_url=watcher)
                _upload_images(watcher, watcher_history, key, temp_dir, cap_md5)
                watcher_history.changed = True
                watcher_history.save()
                watcher.changes += 1
                watcher.last_change = timezone.now()
                bucket = s3_conn.get_bucket(settings.BUCKET_NAME_DAY)
                key_small = bucket.get_key(
                    path(watcher_history.cap_path) / settings.SMALL_PREFIX + settings.CAP_FNAME)
                cap_url_small = re.sub(r'\?x-amz-security-token.*', '', key_small.generate_url(expires_in=0, query_auth=False))
                watcher.last_capture = cap_url_small
                watcher.save()
                if watcher.save_output:
                    watcher_history.output += out
                    watcher_history.save()
                # There has been a change, send notifcations
                notifications = watcher.notifications.all()
                logger.info("Sending {num} notifications for {url}".format(num=len(notifications), url=watcher.url))
                if notifications:
                    html_message = change_msg(watcher, watcher_history)
                    message = html2text(html_message)
                    for notification in notifications:
                        html_message_w_email = html_message.format(email=quote_plus(notification.email))
                        send_mail(
                            subject='page-watch notification for {url}'.format(url=watcher.url),
                            message=message,
                            html_message=html_message_w_email,
                            from_email='no-reply@page-watch.com',
                            recipient_list=[notification.email],
                            fail_silently=False)
            else:
                # No changes, do nothing
                pass

    except Exception as e:
        temp_dir.rmtree()
        _watcher_error(watcher, watcher_history, str(e), out)
        raise

    temp_dir.rmtree()


@app.task
def check_url_day(url, img=True):
    logger.info("checking URL {}".format(url))
    _check_url(url, img)
