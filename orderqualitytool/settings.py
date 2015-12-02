import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '(d!y31^rnwjhux$nwv26*g#z-=_a&gwq0lc1b@3t!gv)dhn_bx'
DEBUG = True
ALLOWED_HOSTS = []
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap3',
    'locations',
    'dashboard',
    'qdbauth',
    'password_reset',
    'raven.contrib.django.raven_compat',
    'admirarchy',
    'menu',
    'rest_framework',
    'django.contrib.sites',
    'custom_user'
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'orderqualitytool.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'orderqualitytool.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', 'qdb'),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASS', ''),
        'HOST': os.environ.get('DB_SERVICE', ''),
        'PORT': os.environ.get('DB_PORT', '')
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Kampala'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/logout'
STATIC_ROOT = 'asset_files'

EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = os.environ.get('EMAIL_PORT', '')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
RAVEN_CONFIG = {
    'dsn': os.environ.get('SENTRY_DSN', None),
}

BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

AUTH_USER_MODEL = 'dashboard.DashboardUser'
try:
    from local_settings import *
except ImportError:
    pass

if ('test' in sys.argv) or ('jenkins' in sys.argv):
    DATABASES = {
        'default':
            {'ENGINE': 'django.db.backends.sqlite3',
             'NAME': 'test_sqlite.db'}
    }
    MEDIA_ROOT = 'media/test'
    PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',
                        'django.contrib.auth.hashers.SHA1PasswordHasher',)
    MEDIA_URL = "/media/"
    STATIC_URL = "/static/"
