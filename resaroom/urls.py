# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views

from resaroom.views import *

urlpatterns = patterns ('',
    (r'^$', room_list, {'tmpl': 'room/list.html'}),
    url(r'^list/(?P<place>\w+)(/(?P<date>\d{4}-\d{1,2}-\d{1,2}))?$', room_detail,
        {'tmpl': 'room/detail.html', 'printmode': False}),
    url(r'^print/(?P<place>\w+)(/(?P<date>\d{4}-\d{1,2}-\d{1,2}))?$', room_detail,
        {'tmpl': 'room/print.html', 'printmode': True}),
)
