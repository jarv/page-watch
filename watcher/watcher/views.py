from rest_framework.views import APIView
from django.core.mail import send_mail
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from tasks import get_screenshot
from watcher.models import WatcherUrl, WatcherUrlNotifications, WatcherUrlHistoryDay
from .util import url_parse, RequestParseFail, human_deltas
from .notification import welcome_msg
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from path import path
from hashids import Hashids
import logging
import boto
import re
from rest_framework.throttling import UserRateThrottle
# import redis
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.cache import cache
from django.views.decorators.cache import never_cache
from urllib import quote_plus
from html2text import html2text

logger = logging.getLogger(__name__)
hasher = Hashids(salt=settings.SECRET_KEY)
# redis_client = redis.Redis(host=settings.REDIS_HOST,
#                            port=settings.REDIS_PORT,
#                            db=settings.REDIS_DB)


class PostRateThrottle(UserRateThrottle):
    scope = 'post_limit'


class GetRateThrottle(UserRateThrottle):
    scope = 'get_limit'


class GetUrlChanges(Feed):

    def __call__(self, request, *args, **kwargs):
        # Cache the RSS feed
        # It has to be done this way because the Feed class is a callable, not a view.
        cache_key = self.get_cache_key(*args, **kwargs)
        response = cache.get(cache_key)

        if response is None:
            response = super(GetUrlChanges, self).__call__(request, *args, **kwargs)
            cache.set(cache_key, response, 900)  # cache for 15 minutes

        return response

    def get_cache_key(self, *args, **kwargs):
        # Override this in subclasses for more caching control
        return "%s-%s" % (self.__class__.__module__, '/'.join(["%s,%s" % (key, val) for key, val in kwargs.items()]))

    def get_object(self, request, hid):

        if not hid:
            raise Http404()
        try:
            ids = hasher.decrypt(hid)
            obj = get_object_or_404(WatcherUrl, id=ids[0])
        except IndexError:
            raise Http404()

        return obj

    def title(self, obj):
        return "Watching for changes on {url} every {interval}".format(
            url=obj.url.replace('http://', '').replace('https://', ''),
            interval=obj.interval)

    def link(self, obj):
        return '{base}/#i/{hid}'.format(
            base=settings.SITE_BASE,
            hid=hasher.encrypt(obj.id))

    def item_link(self, obj):
        return '{base}/#i/{hid}'.format(
            base=settings.SITE_BASE,
            hid=hasher.encrypt(obj.watcher_url.id, obj.id))

    def description(self, obj):
        return "Periodically watching {url} for changes every {interval}".format(
            url=obj.url.replace('http://', '').replace('https://', ''),
            interval=obj.interval)

    def item_description(self, obj):
        pwlink = "{base}/#i/{hid}".format(
            base=settings.SITE_BASE,
            hid=hasher.encrypt(obj.watcher_url.id, obj.id))
        rss_entry = """
            Change detected on {created}<br />
            <a href="{pwlink}"><img src="https://{bucket_name}.s3.amazonaws.com/{cap_path}/{current_fname}" alt="" /></a>
            <a href="{pwlink}"><img src="https://{bucket_name}.s3.amazonaws.com/{cap_path}/{last_fname}" alt="" /></a>
        """.format(
                    created=obj.created,
                    bucket_name=settings.BUCKET_NAME_DAY,
                    cap_path=obj.cap_path,
                    current_fname=settings.SMALL_PREFIX + settings.CAP_HIGHLIGHT_FNAME,
                    last_fname=settings.SMALL_PREFIX + settings.LAST_CAP_HIGHLIGHT_FNAME,
                    pwlink=pwlink,
        )

        return rss_entry

    def item_title(self, obj):
        return "Change detected for {url}".format(
            url=obj.watcher_url.url.replace('http://', '').replace('https://', ''))

    def items(self, obj):
        histories = WatcherUrlHistoryDay.objects.filter(watcher_url=obj, status='processed', changed=True).order_by('-id')[:10]
        for h in histories:
            h.interval = obj.interval
        return histories


class SubscribeUrl(APIView):

    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)

    def _handle_subscription(self, hid, email, subscribe):
        # Handles both unsubscribe and subscribe requests
        # Returns a tuple consisting of the watcher object
        # for the given id and a status dictionary

        ids = hasher.decrypt(hid)

        try:
            watcher = WatcherUrl.objects.get(id=ids[0])
        except WatcherUrl.DoesNotExist:
            logger.warning("Unable to lookup watcher object for id {id}".format(id=ids[0]))
            return (None, dict(
                status='errored',
                reason='Invalid URL'))
        except IndexError:
            logger.warning("Unable to decrypt hid {hid}".format(hid=hid))
            return (None, dict(
                status='errored',
                reason='Invalid URL'))

        try:
            validate_email(email)
        except ValidationError:
            logger.warning("Email validation failed: {email}".format(email=email))
            return (watcher, dict(
                status='errored',
                reason='Invalid email'))

        if subscribe:
            logger.info("Subscribing {email} to {url}".format(
                email=email,
                url=watcher.url))
            notification, created = WatcherUrlNotifications.objects.get_or_create(email=email)
            if created:
                notification.save()
            if watcher.notifications.filter(email=email).exists():
                logger.warning("User {email} re-subscribing to {url}".format(
                    email=email, url=watcher.url))
                return (watcher, dict(
                    status='info',
                    reason='You are already subscribed to this page'))
            else:
                watcher.notifications.add(notification)
                watcher.save()

        else:
            try:
                notification = WatcherUrlNotifications.objects.get(email=email)
                if not watcher.notifications.filter(email=email).exists():
                    logger.warning("{email} trying to unsubscribe from unsubscribed {url}".format(
                        email=email,
                        url=watcher.url))
                    return (watcher, dict(
                        status='errored',
                        reason='You are not subscribed'))
                else:
                    watcher.notifications.remove(notification)
                    watcher.save()
            except WatcherUrlNotifications.DoesNotExist:
                logger.warning("Unable to lookup user {email}".format(email=email))
                return (watcher, dict(
                    status='errored',
                    reason='Email does not exist'))

        return (watcher, dict(
            status='processed',
            url=watcher.url))

    def post(self, request):
        try:
            url, hid, img = _get_request_data(request, 'POST')
        except RequestParseFail as e:
            return Response(dict(
                status='errored',
                reason=str(e)))
        email = request.DATA.get('email', None)
        watcher, d = self._handle_subscription(hid, email, subscribe=True)
        d.update(dict(email=email, hid=hid))
        if watcher and d.get('status') == 'processed':
            # successful subscription, send notification mail
            html_message = welcome_msg(watcher)
            html_message = html_message.format(email=quote_plus(email))
            message = html2text(html_message)
            send_mail(
                subject='Receiving page-watch notifications for {url}'.format(url=watcher.url),
                message=message,
                html_message=html_message,
                from_email='no-reply@page-watch.com',
                recipient_list=[email],
                fail_silently=False)
            logger.info("{email} will receive notifications for {url}".format(email=email, url=watcher.url))
        return(Response(d, template_name="blank.html"))

    @never_cache
    def get(self, request):
        try:
            url, hid, img = _get_request_data(request, 'GET')
        except RequestParseFail as e:
            return Response(dict(
                status='errored',
                reason=str(e)))
        email = request.GET.get('email', None)
        watcher, d = self._handle_subscription(hid, email, subscribe=False)
        d.update(dict(email=email, hid=hid))
        return(Response(d, template_name="unsubscribe.html"))


class CreateUrl(APIView):

    throttle_classes = (PostRateThrottle,)
    renderer_classes = (JSONRenderer, )

    def post(self, request):

        try:
            url, hid, img = _get_request_data(request, 'POST')

        except RequestParseFail as e:
            return Response(dict(
                status='errored',
                reason=str(e)))

        if not url:
            # POST always requires a URL
            return Response(dict(
                status='errored',
                reason='invalid url'))

        # queued_tasks = _get_queued_tasks()

        # if queued_tasks >= settings.MAX_QUEUED_TASKS:
        #     return Response(dict(
        #         status='errored',
        #         reason='Too many queued screenshots ({}), please try again later'.format(queued_tasks))
        #     )

        # for posts always look up by the url passed in
        watcher, created = WatcherUrl.objects.get_or_create(url=url, img=img)
        histories = _get_watcher_with_history(watcher)

        if created or not histories:
            # first time created or initial screenshot failed
            watcher.status = WatcherUrl.STATUS.queued
            watcher.capture_tool = WatcherUrl.CAPTURE_TOOLS.phantomjs
            watcher.save()

            get_screenshot.delay(url=url, img=img)

            return Response(dict(
                url=url,
                hid=hasher.encrypt(watcher.id),
                interval=watcher.interval,
                status=WatcherUrl.STATUS.queued))
        else:
            # For actively monitored pages return
            # the histories
            # Reset the max checks for when we get a post
            watcher.checks_remaining = settings.MAX_CHECKS
            histories['checks_remaining'] = settings.MAX_CHECKS
            return Response(histories)


class CheckUrl(APIView):
    """
    Checks a URL
    """

    throttle_classes = (GetRateThrottle,)
    renderer_classes = (JSONRenderer, )

    @never_cache
    def get(self, request):

        try:
            url, hid, img = _get_request_data(request, 'GET')
        except RequestParseFail as e:
            return Response({
                'status': 'errored',
                'reason': str(e)})

        ids = hasher.decrypt(hid)

        try:
            watcher = WatcherUrl.objects.get(id=ids[0])
        except WatcherUrl.DoesNotExist:
            logger.warning("Unable to lookup url with id {ids}".format(ids=ids))
            return Response(dict(
                status='errored',
                reason='Invalid URL'))
        except IndexError:
            logger.warning("Invalid hashid {hid}".format(hid=hid))
            return Response(dict(
                status='errored',
                reason='Invalid ID'))

        if watcher.screen_grab:
            wh_id = None
            if len(ids) == 2:
                wh_id = ids[1]
            histories = _get_watcher_with_history(watcher, wh_id)
            if histories:
                return Response(histories)
            else:
                logger.error("No histories returned for url:{url} wh_id:{wh_id}".format(
                    url=watcher.url,
                    wh_id=wh_id))
                return Response(dict(
                    status='errored',
                    reason='Invalid ID'))
        elif watcher.status == 'errored':
            logger.error("Critical failure for url: {url}".format(
                url=watcher.url))
            return Response(dict(
                status='errored',
                reason='Invalid URL'))
        else:
            return Response(dict(
                url=watcher.url,
                # queued_tasks=_get_queued_tasks(),
                queued_tasks=0,
                status=watcher.status))


# def _get_queued_tasks():
#     return redis_client.llen(settings.SCREENSHOT_QUEUE)


def _get_request_data(request, req_type):

    if req_type == 'POST':
        req = request.DATA
    elif req_type == 'GET':
        req = request.GET
    else:
        raise RequestParseFail('invalid request type')
    url = req.get('url', None)
    hid = req.get('hid', None)
    img = req.get('img', None)

    if img == "yes":
        img = True
    elif img == "no":
        img = False
    else:
        # enable img checking
        # by default
        img = True

    if url:
        url = url_parse(url)

    return url, hid, img


def _get_watcher_with_history(watcher, wh_id=None):
    """
    Returns a list of watcher histories given a watcher model
    which is set to collect screenshots at a set interval.
    Returns None if no histories have been collected yet
    """

    if wh_id:
        hid = hasher.encrypt(watcher.id, wh_id)
    else:
        hid = hasher.encrypt(watcher.id)

    try:
        if wh_id:
            watcher_histories = [WatcherUrlHistoryDay.objects.get(id=wh_id)]
        if not wh_id:
            # return the latest N captures (configured in settings)
            watcher_histories = WatcherUrlHistoryDay.objects.filter(watcher_url=watcher, status='processed').order_by('-id')[:settings.NUM_CAPTURES]

    except WatcherUrlHistoryDay.DoesNotExist:
        return None

    if not watcher_histories:
        return None

    last_watcher = watcher_histories[0]
    logger.info("bucket name: {} cap_path: {}".format(settings.BUCKET_NAME_DAY, last_watcher.cap_path))
    s3_conn = boto.connect_s3()
    bucket = s3_conn.get_bucket(settings.BUCKET_NAME_DAY,)

    key = bucket.get_key(
        path(last_watcher.cap_path) / settings.CAP_FNAME)
    key_small = bucket.get_key(
        path(last_watcher.cap_path) / settings.SMALL_PREFIX + settings.CAP_FNAME)
    cap_url = key.generate_url(expires_in=3000)
    # workaround for https://github.com/boto/boto/issues/1477
    cap_url_small = re.sub(r'\?x-amz-security-token.*', '', key_small.generate_url(expires_in=0, query_auth=False))

    prev_captures = []
    for wh in watcher_histories:
        if not wh.changed or wh.status != 'processed':
            continue
        deltas = human_deltas(wh)

        bucket = s3_conn.get_bucket(settings.BUCKET_NAME_DAY,)
        key_highlight = bucket.get_key(
            path(wh.cap_path) / settings.CAP_HIGHLIGHT_FNAME)

        key_last_highlight = bucket.get_key(
            path(wh.cap_path) / settings.LAST_CAP_HIGHLIGHT_FNAME)

        key_highlight_small = bucket.get_key(
            path(wh.cap_path) / settings.SMALL_PREFIX + settings.CAP_HIGHLIGHT_FNAME)

        key_last_highlight_small = bucket.get_key(
            path(wh.cap_path) / settings.SMALL_PREFIX + settings.LAST_CAP_HIGHLIGHT_FNAME)

        prev_captures.append(dict(
            cap_highlight_url=key_highlight.generate_url(expires_in=3000),
            cap_highlight_small_url=re.sub(r'\?x-amz-security-token.*', '', key_highlight_small.generate_url(expires_in=0, query_auth=False)),
            cap_last_highlight_url=key_last_highlight.generate_url(expires_in=3000),
            cap_last_highlight_small_url=re.sub(r'\?x-amz-security-token.*', '', key_last_highlight_small.generate_url(expires_in=0, query_auth=False)),
            created=deltas.get('created', ''),
            updated=deltas.get('updated', ''),
            hid=hasher.encrypt(watcher.id, wh.id),
            interval=watcher.interval,
        ))

    deltas = human_deltas(watcher)

    return(dict(
        url=watcher.url,
        hid=hid,
        created=deltas.get('created', ''),
        updated=deltas.get('updated', ''),
        cap_url=cap_url,
        cap_url_small=cap_url_small,
        last_change=deltas.get('last_change', ''),
        last_check=deltas.get('last_check', ''),
        check_expiration=deltas.get('check_expiration', ''),
        prev_captures=prev_captures,
        interval=watcher.interval,
        img=watcher.img,
        checks=watcher.checks,
        changes=watcher.changes,
        capture_tool=watcher.capture_tool,
        checks_remaining=watcher.checks_remaining,
        unlimited=watcher.unlimited,
        sponsor=watcher.sponsor,
        status='processed'))
