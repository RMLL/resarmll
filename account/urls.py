# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth import views as auth_views
from account.views import register, profile, profile_modify, lostpassword
from django.views.generic.simple import redirect_to

urlpatterns = patterns ('',
    (r'^$', redirect_to, {'url': 'login/'}),

    url(r'^login/$',
        auth_views.login,
        {'template_name': 'account/login.html'},
        name='auth_login'),
    url(r'^logout/$',
        auth_views.logout,
        {'template_name': 'account/logout.html'},
        name='auth_logout'),
    #    url(r'^reset/(?P<hash>\w+)/$',
    #        reset,
    #        name='account_reset'),
    url(r'^register/$',
        register,
        {'template_name': 'account/register.html'},
        name='account_register'),
    url(r'^register/complete/$',
        direct_to_template,
        {'template': 'account/register/complete.html'},
        name='account_register_complete'),
    url(r'^lostpassword/$',
        lostpassword,
        {'template_name': 'account/lostpassword.html'},
        name='account_lostpassword'),
    url(r'^lostpassword/sent/$',
        direct_to_template,
        {'template': 'account/lostpassword/sent.html'},
        name='account_lostpassword_sent'),
    url(r'^profile/$',
        profile,
        {'template_name': 'account/profile.html'},
        name='account_profile'),
    url(r'^profile/modify/$',
        profile_modify,
        {'template_name': 'account/profile/modify.html'},
        name='account_profile'),
)
