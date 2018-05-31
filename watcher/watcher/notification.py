from django.conf import settings
import logging
from hashids import Hashids
from urllib import quote_plus
from .util import human_deltas

logger = logging.getLogger(__name__)
hasher = Hashids(salt=settings.SECRET_KEY)


def welcome_msg(watcher):

    hid = hasher.encrypt(watcher.id)
    deltas = human_deltas(watcher)

    html_message = """<p />

        <h2>You or someone else has requested to receive notifications for visual page changes on {url}</h2>
        <strong>If you do not wish to see future notifications click here to
        <a href="{site_base}/s?hid={hid_encoded}&email={EMAIL_PLACEHOLDER}">unsubscribe</a>.</strong>
        <br />
        <i>This page is monitored periodically and if there are many changes you may receive emails as often as once a {interval}</i>
        <p />
        <h3>Most recent screenshot for <a href="{pwlink}">{url}</a> captured {last_check}</h3>
        <a href="{pwlink}"><img src="{last_capture}" /></a>
        <p />
        This page-watch will {check_expiration}.<br /><br />
        Cheers! -<a href="{site_base}">pagewatch.com</a>
        <br />
        <i>page-watch.com is currently in alpha, if you have questions please email <a href="mailto:info@page-watch.com">info@page-watch.com</a></i><br />
        Click here to <a href="{site_base}/s?hid={hid_encoded}&email={EMAIL_PLACEHOLDER}">unsubscribe</a>
    """.format(
        EMAIL_PLACEHOLDER="{email}",
        url=watcher.url,
        interval=watcher.interval,
        pwlink="{}#i/{}".format(settings.SITE_BASE, hid),
        site_base=settings.SITE_BASE,
        last_capture=watcher.last_capture,
        hid_encoded=quote_plus(hid),
        check_expiration=deltas.get('check_expiration', ''),
        last_check=deltas.get('last_check', ''))

    return html_message


def change_msg(watcher, watcher_history):

    direct_hid = hasher.encrypt(watcher.id, watcher_history.id)
    hid = hasher.encrypt(watcher.id)
    deltas = human_deltas(watcher)
    before_img = "https://{bucket_name}.s3.amazonaws.com/{cap_path}/{last_fname}".format(
        bucket_name=watcher_history.bucket_name,
        cap_path=watcher_history.cap_path,
        last_fname=settings.SMALL_PREFIX + settings.LAST_CAP_HIGHLIGHT_FNAME)
    after_img = "https://{bucket_name}.s3.amazonaws.com/{cap_path}/{current_fname}".format(
        bucket_name=watcher_history.bucket_name,
        cap_path=watcher_history.cap_path,
        current_fname=settings.SMALL_PREFIX + settings.CAP_HIGHLIGHT_FNAME)

    html_message = """<p />
        <h2>There has been a change detected on {url}</h2>
        <strong>If you do not wish to see future notifications click here
        to <a href="{site_base}/s?hid={hid}&email={EMAIL_PLACEHOLDER}">unsubscribe</a>.</strong>
        <p />
        <i>This page is monitored every {interval} and was last checked on {last_check}</i>
        <p />
        <b>Click the images below to go to <a href="{pwlink}">view the differences</a>:</b>
        <p />

        <table>
        <tr>
        <td><a href="{pwlink}"><img src="{before_img}" /></a></td>
        <td><a href="{pwlink}"><img src="{after_img}" /></a></td>
        </tr>
        </table>

        <p />
        <h3>Page watch stats for {url}</h3>
        <ul>
            <li>Interval: Every {interval}</li>
            <li>Last successful check: {last_check}</li>
            <li>Last change: {last_change}</li>
            <li># of changes detected: {num_changes}</li>
        </ul>
        <strong>This page-watch will {check_expiration}</strong>
        <p />
        Cheers! -pagewatch
        <br />
        <a href="{site_base}/s?hid={hid}&email={EMAIL_PLACEHOLDER}">unsubscribe</a>
    """.format(
        site_base=settings.SITE_BASE,
        EMAIL_PLACEHOLDER="{email}",
        url=watcher.url,
        interval=watcher.interval,
        pwlink="{}#d/{}".format(settings.SITE_BASE, direct_hid),
        hid=hid,
        last_check=deltas.get('last_check', ''),
        last_change=deltas.get('last_change', ''),
        num_changes=watcher.changes,
        check_expiration=deltas.get('check_expiration', ''),
        before_img=before_img,
        after_img=after_img)
    return html_message
