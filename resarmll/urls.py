# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.views.generic import RedirectView
urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
   (r'^admin/', include(admin.site.urls)),
    (r'^$', RedirectView.as_view(url='account/')),
    (r'^account/', include('account.urls')),
    (r'^resa/', include('resa.urls')),
    (r'^room/', include('resaroom.urls')),
    (r'^utils/', include('resautils.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),
)

