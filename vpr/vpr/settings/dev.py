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

ROOT_URLCONF = 'vpr.urls.dev'

INSTALLED_APPS += (
    'django_extensions',   
    )

TOKEN_REQUIRED = False 
