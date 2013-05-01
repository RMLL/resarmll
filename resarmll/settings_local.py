# -*- coding: utf-8 -*-
import os
PROJECT_DIR = os.path.dirname(__file__)
DOCUMENTSDIR = PROJECT_DIR + '/documents/'
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
### BADGES ###
BADGE_COLORS = False
BADGE_OPACITY = 0.0
BADGE_CITY = ""
BADGE_BG_IMAGE = PROJECT_DIR + '/templates/images/badge-bg.png'
BADGE_BIG_BG_IMAGE = PROJECT_DIR + '/templates/images/badge-bg-big.png'
BADGE_PNG_DEST_DIR = PROJECT_DIR + '/badges/png/'
BADGE_BIG_PNG_DEST_DIR = PROJECT_DIR + '/badges/png/big/'
BADGE_PDF_DEST_DIR = PROJECT_DIR + '/badges/pdf/'
BADGE_WIDTH_MM = 85
BADGE_HEIGHT_MM = 54
ROOMS = {
}
global_httpauth_username = 'rmll'
global_httpauth_password = 'EraoLi7iexa'
### TREASURER ###
TREASURER_SETTINGS = {
    'name': "Pieter Heremans",
    'email': "tresorier@rmll.info",
    'address': """
ABELLI ASBL
Avenue Albert, 240
1190 Forest
Belgique
""",
}

FULL_ADDRESS = """
ABELLI ASBL
Avenue Albert, 240
1190 Forest
Belgique
"""
STATIC_ROOT = '/home/roidelapluie/dev/resa/resarmll/static/'
CURRENCY = 'EUR'
CURRENCY_ALT = None
CART_SETTINGS = {
    # General terms and conditions of sales
    'gcsuse': True,
}
COMPTA_METHOD_CODE_INTERNAL = 'VI'
AUTH_PROFILE_MODULE = 'account.UserProfile'
BANK_DRIVER = 'OGONE'
OGONE_SETTINGS = {
    #
    # tests
    #
    'testmode': True,
    'server': 'https://secure.ogone.com/ncol/test/orderstandard.asp',
    #
    # prod
    #
    #'testmode': False,
    #'server': 'https://secure.ogone.com/ncol/prod/orderstandard.asp',

    'pspid': 'rmll2013',
    'currency': 'EUR',
    'secretkey-in': 'eig0eiG*ohch9phaesh}ohgh6shux8aefoo5chai',
    'secretkey-out': 're8aeBeequ1uavuno5ao2ohphe-ochoh4iethohx',
    'hashtype': 'sha1', # sha1, sha256 or sha512
    'accepturl': '/resa/orders/ogone/return/accept',
    'declineurl': '/resa/orders/ogone/return/decline',
    'exceptionurl': '/resa/orders/ogone/return/exception',
    'cancelurl': '/resa/orders/ogone/return/cancel',
}
### ROOMS ###
ROOMS = {
        }
COMPTA_PLAN_CLIENT_CODE=1
