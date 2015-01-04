import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# CONVENIENCE
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'CET'

# SECURITY
SECRET_KEY = 'ReplaceThisWithYourOwnSecret'
ALLOWED_HOSTS = ['0.0.0.0']

# FILE LOCATIONS
AGV_DATA_DIR = os.path.join(BASE_DIR, 'data')
AGV_SNAP_DIR = os.path.join(AGV_DATA_DIR, 'snapshot')
AGV_REPO_DIR = os.path.join(AGV_DATA_DIR, 'repository')
AGV_THMB_DIR = os.path.join(AGV_DATA_DIR, 'thumbnails')

# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'localhost',
        'NAME': 'argyver',
        'USER': 'angus',
        'PASSWORD': 'Q8nCfYxXL9fT7KmU',
    },
    'development': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(AGV_DATA_DIR, 'database.sqlite3'),
    }
}

# BINARIES
AGV_RSYNC_BIN = '/usr/bin/rsync'

# YOU SHOULD NOT HAVE TO EDIT THE SETTINGS BELOW #

AGV_VERSION = '4.0.0'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'argyver',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'argyver.urls'

WSGI_APPLICATION = 'argyver.wsgi.application'

USE_I18N = True
USE_L10N = True
USE_TZ = True

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
    AGV_DATA_DIR,
)

STATIC_URL = '/static/'
