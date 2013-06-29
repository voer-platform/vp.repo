from django.conf.urls import patterns, url, include
from django.contrib import admin

from vpr_content import views as content_views
from vpr_storage import views as storage_views

import views

urlpatterns = patterns('',
    url(r'^auth/(?P<cid>\w+)/$', views.authenticate, name='authenticate'),
    url(r'^token/(?P<token>\w+)/$', views.testTokenView, name='validate-token'),
    url(r'^materials/$', content_views.MaterialList.as_view(), name='material-list'),
    url(r'^materials/(?P<mid>[0-9a-z]+)/all/$', content_views.MaterialList.as_view(), name='material-version-list'),
    url(r'^materials/(?P<mid>[0-9a-z]+)/((?P<version>\d+)/)?$', content_views.MaterialDetail.as_view(), name='material-detail'), 
    url(r'^materials/(?P<mid>[0-9a-z]+)/((?P<version>\d+)/)?pdf/$', storage_views.getMaterialPDF, name='material-pdf'), 
    url(r'^materials/(?P<mid>[0-9a-z]+)/((?P<version>\d+)/)?mfiles/$', content_views.listMaterialFiles, name='material-file-list'), 
    url(r'^mfiles/(?P<mfid>\d+)?/$', content_views.MaterialFiles.as_view(), name='material-file'), 
    url(r'^mfiles/(?P<mfid>\d+)?/get/?$', storage_views.getMaterialFile, name='get-material-file'), 
    url(r'^authors/$', content_views.AuthorList.as_view(), name='author-list'),
    url(r'^authors/(?P<pk>[0-9]+)/$', content_views.AuthorDetail.as_view(), name='author-detail'),
    url(r'^categories/$', content_views.CategoryList.as_view(), name='category-list'),
    url(r'^categories/(?P<pk>[0-9]+)/$', content_views.CategoryDetail.as_view(), name='category-detail'),
    url(r'^editors/$', content_views.EditorList.as_view(), name='editor-list'),
    url(r'^editors/(?P<pk>[0-9]+)/$', content_views.EditorDetail.as_view(), name='editor-detail'),
    url(r'^persons/$', content_views.PersonList.as_view(), name='person-list'),
    url(r'^persons/(?P<pk>[0-9]+)/$', content_views.PersonDetail.as_view(), name='person-detail'),
    url(r'^search/(?P<keyword>.+)/$', content_views.GeneralSearch.as_view(), name='general-search'),
    )

