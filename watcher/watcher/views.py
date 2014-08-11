from django.http import Http404
from django.conf import settings
from urlparse import urlparse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tasks import check_github_url
from djcelery.models import PeriodicTask, IntervalSchedule
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.contrib.syndication.views import FeedDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
import time
import json
from os.path import basename
from watcher.models import WatcherGithub, WatcherGithubHistory, WatcherGithubNotifications
from .util import path_github_parse, PathParseFail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class GetGithubChanges(Feed):
    """
    Commits since last change
    """
    def get_object(self, request, gh_path):
        try:
            user, repo, branch, file_path, gh_path = path_github_parse(gh_path)
        except PathParseFail as e:
            raise
        return get_object_or_404(WatcherGithub, gh_path=gh_path)

    def title(self, obj):
        return "GH updates for {} ({})".format(basename(obj.gh_path[1:]), obj.repo)

    def link(self, obj):
        return obj.get_absolute_url()

    def item_link(self, obj):
        return obj.get_absolute_url()


    def description(self, obj):
        return "Periodically watches a single github location for changes"

    def item_description(self, obj):
        if obj.commits == '':
            commit = json.loads(obj.commit)
            rss_entry = """Last commit seen is <a href="{html_url}">{sha}</a> with comment <i>{commit_msg}</i>""".format(
                    location=obj.watchergithub.gh_path,
                    html_url=commit['html_url'],
                    commit_msg=commit['commit']['message'],
                    sha=commit['sha'][:8])
            return rss_entry
        else:
            diff = obj.diff
            commits = json.loads(obj.commits)
            rss_entry = """
            Changes detected for {location} - <a href="{diff_link}">diff</a>
            <ul>
            """

            for commit in commits:
                rss_entry += """
                <li>
                    <img alt="{login}" src="{avatar_url}" /> - <a href="{author_html_url}">{login}</a> - <a href="{html_url}">{sha}</a> - <i>{commit_msg}</i>
                </li>
                """.format(
                    login=commit['author']['login'],
                    avatar_url=commit['author']['avatar_url'],
                    author_html_url=commit['author']['html_url'],
                    html_url=commit['html_url'],
                    sha=commit['sha'][:8],
                    commit_msg=commit['commit']['message'])

            rss_entry += """
            </ul>
            """
            return rss_entry
    def item_title(self, obj):
        commit = json.loads(obj.commit)
        return """Changes made by user {login} - {commit_msg}""".format(
            login=commit['author']['login'],
            commit_msg=commit['commit']['message'])

    def items(self, obj):
        return WatcherGithubHistory.objects.filter(watchergithub=obj).order_by('-id')[:30]

class Notify(APIView):
    """
    Subscribes a user to a github path check
    """
    def post(self, request):
        gh_path = request.DATA.get('gh_path', None)
        email = request.DATA.get('email', None)

        if not gh_path or not email:
            return Response({
                'status': 'errored',
                'reason': 'You must pass in a github path and email'})
        try:
            validate_email(email)
        except ValidationError:
            return Response({
                    'status': 'errored',
                    'reason': 'Invalid email'})

        try:
            user, repo, branch, file_path, gh_path = path_github_parse(gh_path)
        except PathParseFail as e:
            return Response({
                'status': 'errored',
                'reason': str(e)})
            raise

        try:
            watcher = WatcherGithub.objects.get(gh_path=gh_path)
        except WatcherGithub.DoesNotExist:
            return Response({
                    'status': 'errored',
                    'reason': 'Github path does not exist'})

class CheckGithubUrl(APIView):
    """
    Checks a github URL
    """

    def get(self, request):

        gh_path = request.GET.get('gh_path', None)
        if not gh_path:
            return Response({
                'status': 'errored',
                'reason': 'You must pass in a github path'})

        try:
            user, repo, branch, file_path, gh_path = path_github_parse(gh_path)
        except PathParseFail as e:
            return Response({
                'status': 'errored',
                'reason': str(e)})
            raise
        url = "https://github.com{}".format(gh_path)
        try:
            watcher = WatcherGithub.objects.get(gh_path=gh_path)
        except WatcherGithub.DoesNotExist:
            return Response(dict(status='DoesNotExist'))

        if watcher.status in [WatcherGithub.STATUS.processing, WatcherGithub.STATUS.initialized]:
            return Response(dict(
                gh_path=gh_path,
                status='processing'))
        elif watcher.status == 'processed':
            return Response(_get_watcher_with_history(watcher))

        else:
            return Response(dict(
                status='errored',
                reason='Unable to check URL'))

    def post(self, request):
        gh_path = request.DATA.get('gh_path', None)
        email = request.DATA.get('email', None)


        if not gh_path:
            return Response({
                'status': 'errored',
                'reason': 'You must pass in a gh_path'})
        try:
            user, repo, branch, file_path, gh_path = path_github_parse(gh_path)
        except PathParseFail as e:
            print str(e)
            return Response({
                'status': 'errored',
                'reason': str(e)})

        url = "https://github.com{}".format(gh_path)
        watcher, created = WatcherGithub.objects.get_or_create(gh_path=gh_path)

        if email:
            print "Email!! {}".format(email)
            notification, created = WatcherGithubNotifications.objects.get_or_create(email=email)
            notification.save()
            watcher.notifications.add(notification)
            watcher.save()
            return Response({'status': 'processed'})


        else:
            if created or watcher.status != WatcherGithub.STATUS.processed:
                watcher.status = WatcherGithub.STATUS.initialized
                watcher.location = url
                watcher.user = user
                watcher.repo = repo
                watcher.branch = branch
                watcher.file_path = file_path
                watcher.save()
                check_github_url.delay(gh_path=gh_path)
                resp = dict(
                    gh_path=gh_path,
                    status='processing')
                return Response(resp)
            else:
                return Response(_get_watcher_with_history(watcher))

def _get_watcher_with_history(watcher):
    watcher_history = WatcherGithubHistory.objects.filter(watchergithub=watcher).order_by('-id')[0]
    commit = json.loads(watcher_history.commit)
    if 'committer' not in commit or not commit['committer']:
        committer = {}
    else:
        committer = commit['committer']
    resp = dict(
        gh_path=watcher.gh_path,
        location=watcher.location,
        user=watcher.user,
        repo=watcher.repo,
        branch=watcher.branch,
        commit_avatar_url=committer.get('avatar_url', '/imgs/github-anon.png'),
        html_url=commit.get('html_url', 'https://github.com'),
        commit_msg=commit.get('commit', {}).get('message', 'No commit message'),
        sha=commit['sha'][:8],
        created=str(watcher_history.created),
        #created=time.mktime(watcher_history.created.timetuple()),
        updated=str(watcher_history.updated),
        #updated=time.mktime(watcher_history.updated.timetuple()),
        status='processed')
    return resp

