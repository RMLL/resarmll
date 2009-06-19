# -*- coding: utf-8 -*-
import os, sys

sys.stdout = sys.stderr

project_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'resarmll.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
