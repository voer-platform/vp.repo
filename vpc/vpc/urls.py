from django.conf.urls import patterns, url, include
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from vpc_api.views import UserList, UserDetail, GroupList, GroupDetail

admin.autodiscover()

urlpatterns = patterns('vpc_api.views',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'api_root'),
    url(r'^users/$', UserList.as_view(), name='user-list'),
    url(r'^users/(?P<pk>\d+)/$', UserDetail.as_view(), name='user-detail'),
    url(r'^groups/$', GroupList.as_view(), name='group-list'),
    url(r'^groups/(?P<pk>\d+)/$', GroupDetail.as_view(), name='group-detail'),
)

# Format suffixes
#urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])

urlpatterns += patterns('',
    url(r'^[0-9]+\.?[0-9]*/', include('vpc_api.urls'),)
    #url(r'^token/(?P<cid>\w+)/$', api_views.getActiveToken, name='get-token'),
    )

urlpatterns += patterns('',
    (r'^grappelli/', include('grappelli.urls')),
    )

# Default login/logout views
urlpatterns += patterns('',
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    )