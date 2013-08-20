# Django settings for vpr project.
import os

SETTING_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.join(SETTING_DIR, '../..')

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT ='/collected-static'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/s/'

# Additional locations of static files
STATICFILES_DIRS = (
    #os.path.join(SETTING_DIR, '../../static'),
    #os.path.join(SETTING_DIR, '../../rest_framework/static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'kw7#s$8t&amp;6d9*7*$a$(gui0r1ze7f#u%(hua=^a3u66+vyj+9g'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# overrided by dev and prod
#ROOT_URLCONF = 'vpr.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'vpr.wsgi.application'


TEMPLATE_DIRS = (
    os.path.join(SETTING_DIR, '../../vpr_admin/templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'rest_framework',
    'south',
    'gunicorn',
#    'raven.contrib.django.raven_compat',
    'haystack',
    'vpr_api',
    'vpr_content',
    'vpr_storage',
    'vpr_admin',    
    'vpr_log',
    )

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        },
#        'sentry': {
#            'level': 'INFO',
#            'class': 'raven.contrib.django.handlers.SentryHandler',
#        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'vpr.api': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'vpr.dashboard': {
            'handlers': ['console'],            
            'level': 'ERROR',
            'propagate': True,
        },
 
   }
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'PAGINATE_BY': 10
}

INTERNAL_IPS = ('127.0.0.1',)

LOGIN_URL = '/dashboard/login'

# INDEX & SEARCHING 

HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_SITECONF = 'vpr.search_sites'
HAYSTACK_WHOOSH_PATH = os.path.join(os.path.dirname(__file__), 'whoosh_index')

RAVEN_CONFIG = {
    'dsn': 'http://0c540c36128343fa9a723e46d9b755cd:7bf6f5f0b4914533b76dc2a89d816d70@localhost:9000/2',
}

# VOER PLATFORM 

EXPORT_DIR = os.path.join(PROJECT_DIR, 'mexports')
IMAGES_DIR = os.path.join(PROJECT_DIR, 'mimgs')
MATERIAL_FILE_DIR = os.path.join(PROJECT_DIR, 'mfiles')
TEMP_DIR = os.path.join(PROJECT_DIR, 'tmp')

VPT_URL = 'http://dev.voer.vn:6543/'

TOKEN_REQUIRED = True 

VPR_MATERIAL_ROLES = ('author', 'editor', 'licensor', 'maintainer', 'translator', 'contributor')
