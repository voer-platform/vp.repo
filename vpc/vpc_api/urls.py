from django.conf.urls import patterns, url, include
from django.contrib import admin

from vpc_content import views as content_views
import views

urlpatterns = patterns('',
    url(r'^auth/(?P<cid>\w+)/$', views.authenticate, name='authenticate'),
    url(r'^token/(?P<cid>\w+)/$', views.testActiveToken, name='test-token'),
    url(r'^modules/$', content_views.ModuleList.as_view()),
    url(r'^modules/', content_views.ModuleDetail.as_view()),
    url(r'^authors/$', content_views.AuthorList.as_view()),
    url(r'^authors/', content_views.AuthorDetail.as_view()),
    )

