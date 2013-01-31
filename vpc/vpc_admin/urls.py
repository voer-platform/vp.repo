from django.conf.urls import patterns, url, include

import views


urlpatterns = patterns('',
    url(r'^$', views.DashboardView.as_view(), name='dashboard-home'),
    url(r'^login/$', views.loginView, name='dashboard-login'),
    url(r'^logout/$', views.logoutDashboard, name='dashboard-logout'),
)
