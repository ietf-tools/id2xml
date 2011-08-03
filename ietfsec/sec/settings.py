# Django settings for sec project.
# BASE_DIR and "settings_local" are from
# http://code.djangoproject.com/wiki/SplitSettings

import os
import syslog
syslog.openlog("django", syslog.LOG_PID, syslog.LOG_LOCAL0)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = False

ADMINS = (
    ('Ryan Cross', 'rcross@amsl.com'),
)

MANAGERS = ADMINS

# DATABASES defined in settings_local.py

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'PST8PDT'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/a/www/www6s'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://www.ietf.org'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'b%28r-26r$mf45tfg^2z6@t$19$x0q8@zb=d-0_5iiiix=147^'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'sec.context_processors.server_mode',
    'sec.context_processors.revision_info',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'sec.middleware.secauth.SecAuthMiddleware',
)

ROOT_URLCONF = 'sec.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    BASE_DIR + "/templates",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.messages',
    'django.contrib.formtools',
    'form_utils',
    'sec.areas',
    'sec.core',
    'sec.drafts',
    'sec.groups',
    'sec.ipr',
    'sec.liaison',
    'sec.meetings',
    'sec.roles',
    'sec.rolodex',
    'sec.sessions',
    'sec.proceedings',
)


# this is a tuple of regular expressions.  if the incoming URL matches one of
# these, than non secretariat access is allowed.
SEC_AUTH_UNRESTRICTED_URLS = (
    (r'^/sec/$'),
    (r'^/sec/interim/'),
    (r'^/sec/proceedings/'),
    (r'^/sec/sessions/'),
)

# Production settings
GROUP_DESCRIPTION_DIR = '/a/www/www6s/wg-descriptions'
IETFWG_DESCRIPTIONS_PATH = '/a/www/www6s/wg-descriptions'
INTERNET_DRAFT_DIR = '/a/www/ietf-ftp/internet-drafts/'
INTERNET_DRAFT_ARCHIVE_DIR = '/a/www/www6s/draft-archive/'
PROCEEDINGS_DIR = '/a/www/www6s/proceedings/'
SERVER_MODE = 'production'
DEVELOPMENT = False
MAX_UPLOAD_SIZE = 20971520 

# Set the multi-database router
DATABASE_ROUTERS = ['sec.utils.database_routers.DBRouter']

# Put SECRET_KEY in here, or any other sensitive or site-specific
# changes.  DO NOT commit settings_local.py to svn.
try:
    from settings_local import *
except ImportError:
    pass

