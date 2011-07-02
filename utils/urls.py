# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from resarmll.utils.views import *

urlpatterns = patterns ('',
    url(r'^sync$', sync),
    url(r'^ksp$', ksp),
)
