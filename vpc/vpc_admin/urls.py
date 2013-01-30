from django.conf.urls import patterns, url, include
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns

import views


urlpatterns = patterns('',
    url(r'^$', views.DashboardView.as_view(), name='dashboard-home'),
    url(r'^dj-admin$', include(admin.site.urls)),
)
