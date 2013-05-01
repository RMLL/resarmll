# -*- coding: utf-8 -*-
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '/tmp/resarmll2012',          # Or path to database file if using sqlite3.
        'USER': 'resarmll',              # Not used with sqlite3.
        'PASSWORD': 'resarmll',          # Not used with sqlite3.
        'HOST': 'localhost',             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
TIME_ZONE = 'Europe/Paris'
LANGUAGE_CODE = 'fr'
LANGUAGES = (
    (u'fr', u'Français'),
    (u'en', u'English'),
)
ROOT_URLCONF = 'resarmll.urls'
INSTALLED_APPS=(
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'resa',
    'compta',
    'account',
    'utils',
)
