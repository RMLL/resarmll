# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.views.generic.simple import direct_to_template
from django.contrib.auth import views as auth_views

from resarmll.account.views import *

urlpatterns = patterns ('',
    (r'^$', redirect_to, {'url': 'home/'}),

    url(r'^langswitch/$', langcheck, {'redirect': '/account/home/'}),
    url(r'^langchange/$', langcheck, {'redirect': '/account/profile/'}),

    url(r'^login/$', auth_views.login, {'template_name': 'account/login.html'}),
    url(r'^logout/$', auth_views.logout, {'template_name': 'account/logout.html'}),

    url(r'^register/$', register, {'tmpl': 'account/register.html'}),
    url(r'^register/set/(?P<code>\w+)$', register_set, {'redirect': '/account/register/'}),
    url(r'^register/complete/$', direct_to_template,
        {'template': 'account/register_complete.html'}),

    url(r'^password_reset/$', auth_views.password_reset,
        {'template_name': 'account/password_reset.html'}),
    url(r'^password_reset/done/$', auth_views.password_reset_done,
        {'template_name': 'account/password_reset_done.html'}),

    url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        {'template_name': 'account/password_reset_confirm.html'}),
    url(r'^reset/done/$', auth_views.password_reset_complete,
        {'template_name': 'account/password_reset_complete.html'}),

    url(r'^home/$', home, {'tmpl': 'account/home.html'}),
    url(r'^profile/$', profile, {'tmpl': 'account/profile.html'}),
    url(r'^profile/modify/$', profile_modify, {'tmpl': 'account/profile_modify.html'}),
    url(r'^profile/badge/$', profile_badge, {'tmpl': 'account/profile_badge.html'}),

    url(r'^wifi/$', wifi, {'tmpl': 'account/wifi.html'}),

    url(r'^create/$', create, {'tmpl': 'account/create.html'}),
    url(r'^search/$', search, {'tmpl': 'account/search.html'}),
    url(r'^edit/(?P<user_id>\d+)$', edit, {'tmpl': 'account/edit.html'}),
    url(r'^manage_badge/(?P<user_id>\d+)$', manage_badge, {'tmpl': 'account/manage_badge.html'}),

# disable WiFi access
    #url(r'^manage_wifi/(?P<user_id>\d+)$', manage_wifi, {'tmpl': 'account/manage_wifi.html'}),
)
