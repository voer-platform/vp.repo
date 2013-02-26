from django.conf.urls import patterns, url, include

import views


urlpatterns = patterns('',
    url(r'^$', views.DashboardView.as_view(), name='dashboard-home'),
    url(r'^login/$', views.loginView, name='dashboard-login'),
    url(r'^logout/$', views.logoutDashboard, name='dashboard-logout'),
    url(r'^clients/$', views.clientListView, name='client-list'),
    url(r'^clients/add/$', views.clientRegView, name='add-client'),
    url(r'^clients/(?P<client_id>\d+)/$', views.clientEditView, name='view-client'),
    url(r'^tokens/$', views.tokenListView, name='token-list'),
)
