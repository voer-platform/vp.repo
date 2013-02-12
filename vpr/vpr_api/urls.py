from django.conf.urls import patterns, url, include
from django.contrib import admin

from vpr_content import views as content_views
import views

urlpatterns = patterns('',
    url(r'^auth/(?P<cid>\w+)/$', views.authenticate, name='authenticate'),
    url(r'^token/(?P<cid>\w+)/$', views.testActiveToken, name='test-token'),
    url(r'^materials/$', content_views.MaterialList.as_view(), name='material-list'),
    url(r'^materials/(?P<mid>[0-9a-z]+)/all/$', content_views.MaterialList.as_view(), name='material-version-list'),
    url(r'^materials/(?P<mid>[0-9a-z]+)/((?P<version>\d+)/)?$', content_views.MaterialDetail.as_view(), name='material-detail'), 
    #url(r'^materials/(?P<pk>[0-9]+)/$', content_views.MaterialDetail.as_view(), name='material-detail'),
    url(r'^authors/$', content_views.AuthorList.as_view(), name='author-list'),
    url(r'^authors/(?P<pk>[0-9]+)/$', content_views.AuthorDetail.as_view(), name='author-detail'),
    url(r'^categories/$', content_views.CategoryList.as_view(), name='category-list'),
    url(r'^categories/(?P<pk>[0-9]+)/$', content_views.CategoryDetail.as_view(), name='category-detail'),
    url(r'^editors/$', content_views.EditorList.as_view(), name='editor-list'),
    url(r'^editors/(?P<pk>[0-9]+)/$', content_views.EditorDetail.as_view(), name='editor-detail'),
    url(r'^search/(?P<keyword>.+)/$', content_views.GeneralSearch.as_view(), name='general-search'),
    )

