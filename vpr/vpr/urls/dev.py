from base import *
from django.conf.urls import include, patterns, url
from vpr_api import views as api_views

urlpatterns += patterns('',
    url(r'^dev/token/(?P<cid>\w+)/$', api_views.getTokenView),
    )

#if settings.DEBUG:
#    print 'OK'
#    import debug_toolbar
#    urlpatterns += patterns('',
#        url(r'^__debug__/', include(debug_toolbar.urls)),
#    )

#INTERCEPT_REDIRECTS = False
