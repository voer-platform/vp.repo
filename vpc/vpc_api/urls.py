from django.conf.urls import patterns, url, include
from django.contrib import admin

from vpc_content import views as content_views
import views

urlpatterns = patterns('',
    url(r'^auth/(?P<cid>\w+)/$', views.authenticate, name='authenticate'),
    url(r'^token/(?P<cid>\w+)/$', views.testActiveToken, name='test-token'),
    url(r'^modules/$', content_views.ModuleList.as_view(), name='module-list'),
    url(r'^modules/(?P<pk>[0-9]+)$', content_views.ModuleDetail.as_view(), name='module-detail'),
    url(r'^authors/$', content_views.AuthorList.as_view(), name='author-list'),
    url(r'^authors/(?P<pk>[0-9]+)/$', content_views.AuthorDetail.as_view(), name='author-detail'),
    url(r'^categories/$', content_views.CategoryList.as_view(), name='category-list'),
    url(r'^categories/(?P<pk>[0-9]+)/$', content_views.CategoryDetail.as_view(), name='category-detail'),
    url(r'^editors/$', content_views.EditorList.as_view(), name='editor-list'),
    url(r'^editors/(?P<pk>[0-9]+)/$', content_views.EditorDetail.as_view(), name='editor-detail'),
    )

