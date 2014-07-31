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
import json

from watcher.models import WatcherGithub, WatcherGithubHistory
from .util import url_github_parse, PathParseFail

class GetGithubChanges(Feed):
    """
    Commits since last change
    """
    def get_object(self, request, gh_path):
        try:
            user, repo, branch, path = gh_parts_from_path(gh_path)
        except PathParseFail as e:
            raise
        return get_object_or_404(WatcherGithub, gh_path=gh_path)

    def title(self, obj):
        return "Github changes for {}".format(obj.location)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return "Periodically watches a single github location for changes"

    def item_description(self, obj):
        if obj.commits == '':
            commit = json.loads(obj.commit)
            rss_entry = """Last commit seen is for {location} is <a href="{html_url}">{sha}</a> - <i>{commit_msg}</i>""".format(
                    location=obj.watchergithub.location,
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
        return WatcherGithubHistory.objects.filter(watchergithub=obj).order_by('-created')[:30]

class CheckGithubUrl(APIView):
    """
    Checks a github URL
    """

    def get(self, request):
        #url = request.GET.get('url', None)
        #url_parsed = urlparse(url)
        #user, repo, branch, file_path = gh_parts_from_path(url_parsed.path)

        return Response()

    def post(self, request):
        url = request.DATA.get('url', None)
        if not url:
            return Response({
                'error': True,
                'reason': 'You must pass in a url'})
        try:
            user, repo, branch, file_path, gh_path = url_github_parse(url)
        except PathParseFail as e:
            return Response({
                'error': True,
                'reason': 'Unable to check URL'})

        watcher, created = WatcherGithub.objects.get_or_create(gh_path=gh_path)
        if watcher.status != WatcherGithub.STATUS.processed:
            watcher.status = WatcherGithub.STATUS.initialized
            watcher.location = url
            watcher.user = user
            watcher.repo = repo
            watcher.branch = branch
            watcher.file_path = file_path
            watcher.save()
            check_github_url.delay(gh_path=gh_path)
        return Response({
            'path': gh_path,
            'status': 'checking'})
