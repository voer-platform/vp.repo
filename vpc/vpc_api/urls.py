from django.conf.urls import patterns, url, include
from django.contrib import admin
import views

urlpatterns = patterns('',
    url(r'^auth/(?P<cid>\w+)/$', views.authenticate, name='authenticate'),
    url(r'^token/(?P<cid>\w+)/$', views.testActiveToken, name='test-token'),
    )

