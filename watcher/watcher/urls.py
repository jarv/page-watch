from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns
from watcher import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^g/?$', views.CheckGithubUrl.as_view()),
    url(r'^f(?P<gh_path>.*).xml$', views.GetGithubChanges()),
)

urlpatterns = format_suffix_patterns(urlpatterns)
