from django.conf.urls import patterns, url, include
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns

from vpr_api.views import registerClient

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^dashboard/', include('vpr_admin.urls')),
    url(r'^$', 'vpr_api.views.api_root'),
    url(r'^setup/register/$', registerClient, name='register-client'),
)

urlpatterns += patterns('',
    url(r'^[0-9]+\.?[0-9]*/', include('vpr_api.urls'),)
    )

# Default login/logout views
urlpatterns += patterns('',
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    )
