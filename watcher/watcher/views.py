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

class GetGithubChanges(Feed):

    def get_object(self, request):
        url = request.DATA.get('url', None)
        if not url:
            return Response()
        url_parsed = urlparse(url)
        if not url_parsed.netloc.lower().startswith('github'):
            return Response({'error': True, 'reason': 'You can only check a github url'})

        return get_object_or_404(WatcherGithub, location=url_parsed.geturl())

    def title(self, obj):
        return "Changes for {}".format(obj.location)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return "Changes for {}".format(obj.locatino)

    def items(self, obj):
        return WatcherGithubHistory.objects.filter(watchergithub=obj).order_by('-created')[:30]

class CheckGithubUrl(APIView):
    """
    Checks a github URL
    """

    def get(self, request):
        return Response()

    def post(self, request):
        url = request.DATA.get('url', None)
        if not url:
            return Response({
                'error': True,
                'reason': 'You must pass in a url'})

        url_parsed = urlparse(url)

        if url_parsed.scheme not in ['http', 'https']:
            url_parsed = urlparse('https://' + url_parsed.netloc +
                url_parsed.path)

        if not 'github' in url_parsed.netloc.lower():
            return Response({
                'error': True,
                'reason': 'You can only check a github url'})

        # strip everything except the path and
        # set the proto to https
        url = 'https://github.com' + url_parsed.path

        check_github_url.delay(url)

        return Response()
