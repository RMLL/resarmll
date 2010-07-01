# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from resarmll.utils.views import sync

urlpatterns = patterns ('',
    url(r'^sync$', sync),
)
