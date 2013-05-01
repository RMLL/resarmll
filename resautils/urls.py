# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from resautils.views import *

urlpatterns = patterns ('',
    url(r'^sync$', sync),
    url(r'^ksp$', ksp),
)
