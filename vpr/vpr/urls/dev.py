from base import *
from django.conf.urls import patterns, url
from vpr_api import views as api_views

urlpatterns += patterns('',
    url(r'^dev/token/(?P<cid>\w+)/$', api_views.getTokenView),
    )

