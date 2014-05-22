from django.conf.urls import patterns, url, include
from django.contrib import admin

from vpr_content import views as content_views
from vpr_storage import views as storage_views

import views

urlpatterns = patterns('',
    url(r'^auth/(?P<cid>\w+)/?$', views.authenticate, name='authenticate'),
    url(r'^token/(?P<token>\w+)/?$', views.testTokenView, name='validate-token'),
    url(r'^mfiles/(?P<mfid>\d+)/?$', content_views.MaterialFiles.as_view(), name='material-file'), 
    url(r'^mfiles/(?P<mfid>\d+)/get/?$', storage_views.getMaterialFile, name='get-material-file'), 
    url(r'^categories/?$', content_views.CategoryList.as_view(), name='category-list'),
    url(r'^categories/(?P<pk>[0-9]+)/?$', content_views.CategoryDetail.as_view(), name='category-detail'),
    url(r'^persons/?$', content_views.PersonList.as_view(), name='person-list'),
    url(r'^persons/(?P<pk>[0-9]+)/?$', content_views.PersonDetail.as_view(), name='person-detail'),
    url(r'^persons/(?P<pk>[0-9]+)/avatar/?$', storage_views.handlePersonAvatar, name='person-avatar'),
    url(r'^persons/(?P<pk>[0-9]+)/favorites/?$', content_views.get_person_favs, name='person-favorites'),
    )

urlpatterns += patterns('',
    url(r'^materials/?$', content_views.MaterialList.as_view(), name='material-list'),
    url(r'^materials/(?P<mid>[0-9a-z]+)/all/?$', content_views.MaterialList.as_view(), name='material-version-list'),
    url(r'^materials/(?P<mid>[0-9a-z]+)(/(?P<version>\d+))?/?$', content_views.MaterialDetail.as_view(), name='material-detail'), 
    url(r'^materials/(?P<mid>[0-9a-z]+)(/(?P<version>\d+))?/pdf/?$', storage_views.getMaterialPDF, name='material-pdf'), 
    url(r'^materials/(?P<mid>[0-9a-z]+)(/(?P<version>\d+))?/zip/?$', storage_views.getMaterialZip, name='material-zip'), 
    url(r'^materials/(?P<mid>[0-9a-z]+)(/(?P<version>\d+))?/image/?$', content_views.getMaterialImage, name='material-image'), 
    url(r'^materials/(?P<mid>[0-9a-z]+)(/(?P<version>\d+))?/mfiles/?$', content_views.listMaterialFiles, name='material-file-list'), 
    url(r'^materials/(?P<mid>[0-9a-z]+)(/(?P<version>\d+))?/similar/?$', content_views.getSimilarMaterials, name='material-similar'),
    url(r'^materials/(?P<mid>[0-9a-z]+)(/(?P<version>\d+))?/counter/?$', content_views.materialCounterView, name='material-counter'),
    url(r'^materials/(?P<mid>[0-9a-z]+)(/(?P<version>\d+))?/comments/?$', content_views.MaterialComments.as_view(), name='material-comments'),
    url(r'^materials/(?P<mid>[0-9a-z]+)(/(?P<version>\d+))?/rates/?$', content_views.materialRatesView, name='material-rates'),
    url(r'^materials/(?P<mid>[0-9a-z]+)(/(?P<version>\d+))?/favorites/?$', content_views.materialFavoriteView, name='material-favorite'),
    url(r'^materials/(?P<mid>[0-9a-z]+)(/(?P<version>\d+))?/links?$', content_views.material_links_view, name='material-links'),
    )

urlpatterns += patterns('',
    url(r'^stats/materials/counter/?$', content_views.queryMaterialByViewCount, name='stats-most-viewed'),
    url(r'^stats/materials/favorites/?$', content_views.get_most_faved, name='stats-most-faved'),
    url(r'^stats/materials/rates/?$', content_views.get_top_rated, name='stats-top-rated'),
    )

# search & browse urls
urlpatterns += patterns('',
    url(r'^(search|s)/?$', content_views.GeneralSearch.as_view(), name='general-search'),
    url(r'^facet/?$', content_views.facetSearchView, name='facet-search'),
    )
