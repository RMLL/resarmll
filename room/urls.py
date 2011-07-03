# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.views.generic.simple import direct_to_template
from django.contrib.auth import views as auth_views

from resarmll.room.views import *

urlpatterns = patterns ('',
    (r'^$', room_list, {'tmpl': 'room/list.html'}),
    url(r'^list/(?P<place>\w+)(/(?P<date>\d{4}-\d{1,2}-\d{1,2}))?$', room_detail,
        {'tmpl': 'room/detail.html', 'printmode': False}),
    url(r'^print/(?P<place>\w+)(/(?P<date>\d{4}-\d{1,2}-\d{1,2}))?$', room_detail,
        {'tmpl': 'room/print.html', 'printmode': True}),
)
