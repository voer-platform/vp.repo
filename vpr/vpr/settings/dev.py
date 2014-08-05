# Django settings for vpr project.

from base import *

DEBUG = True
DEVELOPMENT = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        #'NAME': 'vpr.sqlite3',                  # Or path to database file if using sqlite3.
        'ENGINE': 'django.db.backends.mysql',    # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'vpr',                  # Or path to database file if using sqlite3.
        'USER': 'vpr',                       # Not used with sqlite3.
        'PASSWORD': 'vpr',                   # Not used with sqlite3.
        'HOST': 'localhost',                 # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Make this unique, and don't share it with anybody.
#SECRET_KEY = 'kw7#s$8t&amp;6d9*7*$a$(gui0r1ze7f#u%(hua=^a3u66+vyj+9g'

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

ROOT_URLCONF = 'vpr.urls.dev'

INSTALLED_APPS += (
    'django_extensions',
    'debug_toolbar',
    )

STATICFILES_DIRS = (
    os.path.join(SETTING_DIR, '../../static'),
    os.path.join(SETTING_DIR, '../../rest_framework/static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)


DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}


VPT_URL = 'http://dev.voer.vn:6543/'

TOKEN_REQUIRED = False
