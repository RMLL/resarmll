# -*- coding: utf-8 -*-

import os

# Django settings for resarmll project.

PROJECT_DIR = os.path.dirname(__file__)

SERVER_EMAIL = 'reservation@rmll.info'
# ADMINS needs to be a list (a tuple make mail_admins fails)
EMAIL_SUBJECT_PREFIX = '[TRACE] '
ADMINS = (
    ('Resa Rmll Team', 'kolter@openics.org'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2' # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'resarmll2011'          # Or path to database file if using sqlite3.
DATABASE_USER = 'resarmll'              # Not used with sqlite3.
DATABASE_PASSWORD = 'resarmll'          # Not used with sqlite3.
DATABASE_HOST = 'localhost'             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''                      # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr-FR'

LANGUAGES = (
    (u'fr', u'Français'),
    (u'en', u'English'),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'NEx}l{s>a!A)q|wgoNCgU?=i8gnl"{cB?yU"OL}qy:TTq$8=FW8rSybKG1#q}(\H'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#    'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'resarmll.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    PROJECT_DIR + '/templates/',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.markup',
#    'django_evolution',
#    'django.contrib.sites',
    'resarmll.resa',
    'resarmll.compta',
    'resarmll.account',
    'resarmll.utils',
)

# template processors
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'resarmll.resa.context_processors.user',
)

#############################################
#############################################
#############################################

### COMMON ###
DOCUMENT_ROOT = PROJECT_DIR + MEDIA_URL

### SESSIONS / COOKIES ###
SESSION_COOKIE_NAME = 'resarmll'
SESSION_COOKIE_AGE = 10800
SESSION_ENGINE = "django.contrib.sessions.backends.file"

### EMAIL CONFIG ###
DEFAULT_FROM_EMAIL = SERVER_EMAIL
DEFAULT_PREFIX_SUBJECT_EMAIL = '[RMLL RESA] '

### ACCOUNT ###
AUTH_PROFILE_MODULE = 'account.UserProfile'
LOGIN_REDIRECT_URL = '/account/langswitch/'
LOGIN_URL = '/account/login/'
LOGOUT_URL = '/account/logout/'

### COMPTA ###
COMPTA_BANK_FIXED_TAX = 0.24
COMPTA_BANK_VARIABLE_TAX = 0.005 # percentage
COMPTA_METHOD_CODE_BANK = 'CBI'
COMPTA_METHOD_CODE_PAYPAL = 'VPP'
COMPTA_METHOD_CODE_INTERNAL = 'VI'
COMPTA_PLAN_CLIENT_CODE = 411

### BADGES ###
BADGE_CITY = "Strasbourg 2011"
BADGE_BG_IMAGE = PROJECT_DIR + '/templates/images/badge-bg.png'
BADGE_BIG_BG_IMAGE = PROJECT_DIR + '/templates/images/badge-bg-big.png'
BADGE_PNG_DEST_DIR = 'badges/png/'
BADGE_BIG_PNG_DEST_DIR = 'badges/png/big/'
BADGE_PDF_DEST_DIR = 'badges/pdf/'
BADGE_PRINTER_PDF_DEST_DIR = 'badges/pdf/printer/'
BADGE_WIDTH_MM = 85
BADGE_HEIGHT_MM = 54
BADGE_PRINTER_WIDTH_MM = 86.0
BADGE_PRINTER_HEIGHT_MM = 54.0

### USERS DB SYNC ###
global_httpauth_username = 'rmll'
global_httpauth_password = 'EraoLi7iex'
global_httpauth_message = 'LSM users sync'

### TREASURER ###
CHECK_SETTINGS = {
    'to': 'Association RMLL Strasbourg',
    'contact_email': SERVER_EMAIL,
}

TREASURER_NAME = "Trésorier RMLL 2011"
TREASURER_EMAIL = "tresorier@2011.rmll.info"

TREASURER_ADDRESS = """
Emmanuel Bouthenot
119 rue Malbec
33800 Bordeaux
FRANCE
"""

CHECK_PAYABLE_TO = CHECK_SETTINGS['to']

### PAYPAL ###
PAYPAL_SETTINGS = {
#
# tests
#
#    'id': 'paypal_1209199069_biz@openics.org',
#    'url': 'https://www.sandbox.paypal.com/cgi-bin/webscr',
#
# prod
#
    'id': '',
    'url' : 'https://www.paypal.com/cgi-bin/webscr',
    'currency': 'EUR',
    'return': '/resa/orders/paypal/return',
    'cancel_return': '/resa/orders/paypal/cancel',
    'notify_url': '/resa/orders/paypal/notify',
}

### Bank Driver ( CyberPlus or eTransactions) ###
BANK_DRIVER = 'cmcic'

### CYBERPLUS ###
CYBERPLUS_SETTINGS = {
    'merchant_id': '',
    #'merchant_id': '038862749811111', #tests
    'merchant_country': 'fr',
    'currency_code': '978', # EURO = 978
    'payment_means': 'CB,1,VISA,1,MASTERCARD,1',
    'normal_return_url': '/resa/orders/cyberplus/return',
    'cancel_return_url': '/resa/orders/cyberplus/return',
    'automatic_response_url': '/resa/orders/cyberplus/notify',
}

### ETRANSACTIONS ###
ETRANSACTIONS_SETTINGS = {
#
# tests
#
#    'site': '1999888',
#    'rang': '98', # tests
#    'identifiant': '3', #tests
#    'testmode': True,

#
# prod
#
    'testmode': False,
    'site': '',
    'rang': '',
    'identifiant': '',
    'mode': '4',
    'devise': '978', # EURO = 978
    'return_url_prefix': '/resa/orders/etransactions/return',
}

### CMCIC ###
CMCIC_SETTINGS = {
#
# tests
#
    'testmode': True,
    'cle': '',
    'tpe': '',
    'version': '3.0',
    'serveur': 'https://paiement.creditmutuel.fr/test/paiement.cgi',
    'codesociete': '',
    'devise': 'EUR',
    'url_ret': '/resa/orders/cmcic/return',
    'url_ok': '/resa/orders/cmcic/return/ok',
    'url_err': '/resa/orders/cmcic/return/err',
#
# prod
#
#    'testmode': False,
#    'cle': '',
#    'tpe': '0000001',
#    'version': '3.0',
#    'serveur': 'https://paiement.creditmutuel.fr/paiement.cgi',
#    'codesociete': '',
#    'devise': 'EUR',
#    'url_ret': '/resa/orders/cmcic/return',
#    'url_ok': '/resa/orders/cmcic/return/ok',
#    'url_err': '/resa/orders/cmcic/return/err',
}

### MISC ###
FULL_ADDRESS = """
Association RMLL Strasbourg - 2011 - contact@2011.rmll.info
S/C Maison des Associations - 1a place des Orphelins - 67000 Strasbourg
SIRET 520 081 431 00014 – Code APE 9499Z
"""

TVA = 0

### DEVELOPMENT SETTINGS ###
if os.environ.has_key('DJANGO_DEVEL'):
    SESSION_COOKIE_NAME += '-dev'
    DEBUG = True
    TEMPLATE_DEBUG = DEBUG

    BADGE_PNG_DEST_DIR = 'tmp/badges/png/'
    BADGE_BIG_PNG_DEST_DIR = 'tmp/badges/png/big/'
    BADGE_PDF_DEST_DIR = 'tmp/badges/pdf/'
    BADGE_PRINTER_PDF_DEST_DIR = 'tmp/badges/pdf/printer/'
else:
    DEBUG = False
    TEMPLATE_DEBUG = False

