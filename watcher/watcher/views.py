from django.http import Http404
from urlparse import urlparse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tasks import add

class CheckUrl(APIView):
    """
    Checks a URL
    """

    def get(self, request):
        return Response()

    def post(self, request):
        url = request.DATA.get('url', None)
        if not url:
            return Response()
        url_parsed = urlparse(url)
        if not url_parsed.path.lower().startswith('github'):
            return Response()

        res = check_url.delay("https://{}".format(url_parsed.path))
        return Response()


#class WebsiteList(APIView):
#    """
#    List all websites
#    """
#
#    def get(self, request, format=None):
#        add.delay(4, 4)
#        websites = Website.objects.all()
#        serializer = WebsiteSerializer(websites, many=True)
#        return Response(serializer.data)
#
#    def post(self, request, format=None):
#        serializer = WebsiteSerializer(data=request.DATA)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#class WebsiteDetail(APIView):
#    """
#    Retrieve, update or delete a website instance
#    """
#    def get_object(self, pk):
#        try:
#            return Website.objects.get(pk=pk)
#        except Website.DoesNotExist:
#            raise Http404
#
#    def get(self, request, pk, format=None):
#        website = self.get_object(pk)
#        serializer = WebsiteSerializer(website)
#        return Response(serializer.data)
#
#    def put(self, request, pk, format=None):
#        website = self.get_object(pk)
#        serializer = WebsiteSerializer(website, data=request.DATA)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#    def delete(self, request, pk, format=None):
#        website = self.get_object(pk)
#        website.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)
