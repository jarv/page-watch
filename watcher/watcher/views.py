from rest_framework.views import APIView
from rest_framework.response import Response
from tasks import check_github_url
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
import json
from os.path import basename
from watcher.models import WatcherGithub, WatcherGithubHistory, WatcherGithubNotifications
from .util import path_github_parse, PathParseFail, get_commit_info


class GetGithubChanges(Feed):
    """
    Commits since last change
    """
    def get_object(self, request, gh_path):
        try:
            user, repo, branch, file_path, gh_path = path_github_parse(gh_path)
        except PathParseFail:
            raise
        return get_object_or_404(WatcherGithub, gh_path=gh_path)

    def title(self, obj):
        return "GH updates for {}".format(basename(obj.gh_path[1:]))

    def link(self, obj):
        return obj.get_absolute_url()

    def item_link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return "Periodically watch {} for changes".format(obj.gh_path[1:])

    def item_description(self, obj):
        rss_entry = "<b>Commits sine the last poll:</b>"

        if obj.diff != '':
            rss_entry += " <a href='{diff}'>(diff)</a>".format(diff=obj.diff)
        rss_entry += "<ul>"
        commits = json.loads(obj.commits)
        for commit in commits:
            sha, login, login_url, name, avatar_url, commit_url, commit_msg = get_commit_info(commit)
            rss_entry += "<li>"
            if login and name and login_url:
                rss_entry += "{name} (<a href='{login_url}'>{login}</a>) ".format(
                    name=name,
                    login_url=login_url,
                    login=login)
            rss_entry += "<a href='{commit_url}'>{sha}</a> - <i>{commit_msg}</i>".format(
                commit_url=commit_url,
                sha=sha[:8],
                commit_msg=commit_msg)

            rss_entry += "</li>"
        rss_entry += "</ul>"

        return rss_entry

    def item_title(self, obj):
        commits = json.loads(obj.commits)
        sha, login, login_url, name, avatar_url, commit_url, commit_msg = get_commit_info(commits[0])
        return """Detected change for {gh_path} made by {name} ({login}) - {commit_msg}""".format(
            gh_path=obj.watchergithub.gh_path[1:],
            name=name,
            login=login,
            commit_msg=commit_msg)

    def items(self, obj):
        return WatcherGithubHistory.objects.filter(watchergithub=obj).order_by('-id')[:30]


#class Notify(APIView):
#    """
#    Subscribes a user to a github path check
#    """
#    def post(self, request):
#        gh_path = request.DATA.get('gh_path', None)
#        email = request.DATA.get('email', None)
#
#        if not gh_path or not email:
#            return Response({
#                'status': 'errored',
#                'reason': 'You must pass in a github path and email'})
#        try:
#            validate_email(email)
#        except ValidationError:
#            return Response({
#                'status': 'errored',
#                'reason': 'Invalid email'})
#
#        try:
#            user, repo, branch, file_path, gh_path = path_github_parse(gh_path)
#        except PathParseFail as e:
#            return Response({
#                'status': 'errored',
#                'reason': str(e)})
#            raise
#
#        try:
#            watcher = WatcherGithub.objects.get(gh_path=gh_path)
#        except WatcherGithub.DoesNotExist:
#            return Response({
#                    'status': 'errored',
#                    'reason': 'Github path does not exist'})

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
    commits = json.loads(watcher_history.commits)
    sha, login, login_url, name, avatar_url, commit_url, commit_msg = get_commit_info(commits[0])

    resp = dict(
        gh_path=watcher.gh_path,
        location=watcher.location,
        user=watcher.user,
        repo=watcher.repo,
        branch=watcher.branch,
        commit_avatar_url=avatar_url,
        comit_url=commit_url,
        commit_msg=commit_msg,
        sha=sha[:8],
        created=str(watcher_history.created),
        updated=str(watcher_history.updated),
        status='processed')
    return resp
