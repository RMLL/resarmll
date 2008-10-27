from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth import views as auth_views

from account.views import register

urlpatterns = patterns ('',
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
        {'template': 'account/register_complete.html'},
        name='account_register_complete'),
)
