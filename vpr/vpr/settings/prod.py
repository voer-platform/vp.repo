# Django settings for vpr project.

from base import *

DEBUG = False
DEVELOPMENT = False 
PRODUCTION = True

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        #'NAME': 'vpr.sqlite3',                  # Or path to database file if using sqlite3.
        'ENGINE': 'django.db.backends.mysql',    # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'vpr',                      # Or path to database file if using sqlite3.
        'USER': 'vpr',                      # Not used with sqlite3.
        'PASSWORD': 'vpr',                  # Not used with sqlite3.
        'HOST': 'localhost',                # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                     # Set to empty string for default. Not used with sqlite3.
    }
}

ROOT_URLCONF = 'vpr.urls.prod'

