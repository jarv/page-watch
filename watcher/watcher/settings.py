"""
Django settings for watcher project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import djcelery
from path import path
from distutils import spawn
from logging.config import dictConfig
import sys
import os

PROJECT_ROOT = path(__file__).abspath().dirname().dirname().dirname()
SERVER_EMAIL = "no-reply@page-watch.com"
ADMINS = (('Jarv', 'info@page-watch.com'),)
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '**redacted**'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []
EMAIL_BACKEND = 'seacucumber.backend.SESBackend'

# This is the default
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': 'unique-snowflake'
#     }
# }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)s %(process)d '
                      '[%(name)s] %(filename)s:%(lineno)d - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': sys.stderr,
        },
    },
    'loggers': {
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django': {
            'handlers': ['console'],
            # 'level': 'ERROR',
            'level': 'DEBUG',
            'propagate': False,
        },
        'watcher': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'seacucumber': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },

    }
}
dictConfig(LOGGING)
# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'djcelery',
    'watcher',
    'debug_toolbar',
    'debug_panel',
    'seacucumber',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'debug_panel.middleware.DebugPanelMiddleware',
)

ROOT_URLCONF = 'watcher.urls'

WSGI_APPLICATION = 'watcher.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'post_limit': '60/min',
        'get_limit': '120/min',
    },
    'EXCEPTION_HANDLER': 'watcher.util.custom_exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': []
}

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'watcher',
        'USER': 'watcher',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
    }
}

DB_OVERRIDES = dict(
    PASSWORD=os.environ.get('DB_PASS', DATABASES['default']['PASSWORD']),
    USER=os.environ.get('DB_USER', DATABASES['default']['USER']),
    NAME=os.environ.get('DB_NAME', DATABASES['default']['NAME']),
    HOST=os.environ.get('DB_HOST', DATABASES['default']['HOST']),
    PORT=os.environ.get('DB_PORT', DATABASES['default']['PORT']),
)

for override, value in DB_OVERRIDES.iteritems():
    DATABASES['default'][override] = value


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

COMPARE_SCRIPT = PROJECT_ROOT / 'util' / 'compare.sh'

CAPTURE_TOOLS = dict(
    phantomjs=spawn.find_executable('phantomjs'),
    wkhtmltoimage=spawn.find_executable('wkhtmltoimage'))

phantom_opts = [
    '--ignore-ssl-errors=yes',
    '--ssl-protocol=any',
    PROJECT_ROOT / 'util' / 'capture.js']

wk_bin_opts = [
    '--width', '1024',
    '--disable-smart-width',
    '--cache-dir', '/tmp/cache',
    '--load-error-handling', 'ignore',
    '--disable-local-file-access']

CAPTURE_OPTS = dict(
    phantomjs=phantom_opts,
    wkhtmltoimage=wk_bin_opts)

TIMEOUTS = dict(
    phantomjs=300,
    wkhtmltoimage=60)

COMPARE_TIMEOUT = 30
CONVERT_BIN = spawn.find_executable('convert')
IDENTIFY_BIN = spawn.find_executable('identify')

CAPTURE_TOOL = 'cutycapt'

IMAGE_EXTENSION = path('.png')

RESIZED_PREFIX = 'resized-'
CAP_FNAME = 'capture' + IMAGE_EXTENSION
CAP_FNAME_RESIZED = RESIZED_PREFIX + CAP_FNAME
LAST_CAP_FNAME = 'last-capture' + IMAGE_EXTENSION
LAST_CAP_FNAME_RESIZED = RESIZED_PREFIX + LAST_CAP_FNAME


MAX_CHECKS = 30

# Generated by the compare script
# These CANNOT be changed
CAP_HIGHLIGHT_FNAME = 'highlighted-' + CAP_FNAME
CAP_NO_IMG_HIGHLIGHT_FNAME = 'highlighted-' + CAP_FNAME

LAST_CAP_HIGHLIGHT_FNAME = 'highlighted-' + LAST_CAP_FNAME
LAST_CAP_NO_IMG_HIGHLIGHT_FNAME = 'highlighted-' + LAST_CAP_FNAME

MASK_FNAME = 'mask' + IMAGE_EXTENSION
MASK_NO_IMG_FNAME = 'mask' + IMAGE_EXTENSION

MASK_BLUR_FNAME = 'mask-blur' + IMAGE_EXTENSION
MASK_BLUR_NO_IMG_FNAME = 'mask-blur' + IMAGE_EXTENSION

MASK_BLUR_MONOCHROME_FNAME = 'mask-blur-monochrome' + IMAGE_EXTENSION
MASK_BLUR_MONOCHROME_NO_IMG_FNAME = 'mask-blur-monochrome' + IMAGE_EXTENSION

MEDIUM_PREFIX = 'medium-'
SMALL_PREFIX = 'small-'
SMALL_HEIGHT = 400
SMALL_WIDTH = 400
# Anything greater than this
# height or width will be cropped
MAX_HEIGHT = 5000
MAX_WIDTH = 2048
###############################

SITE_BASE = 'http://localhost:8000/static/index.html'
MAX_ERRORS = 10

INTERVALS = {
    'one minute': dict(every=1, period='minutes'),
    'five minutes': dict(every=5, period='minutes'),
    'ten minutes': dict(every=10, period='minutes'),
    'fifteen minutes': dict(every=15, period='minutes'),
    'thirty minutes': dict(every=30, period='minutes'),
    'hour': dict(every=60, period='minutes'),
    'day': dict(every=1440, period='minutes'),
    'week': dict(every=10080, period='minutes'),
}

# Number of captures to display
NUM_CAPTURES = 5

BUCKET_NAME_DAY = 'page-watch-day-dev'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = PROJECT_ROOT / 'static' / 'static'
STATICFILES_DIRS = (PROJECT_ROOT / 'static',)

MAX_QUEUED_TASKS = 10
SCREENSHOT_QUEUE = 'screenshot'

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_DB = os.environ.get('REDIS_DB', 0)
RABBIT_PORT = os.environ.get('RABBIT_PORT', 5672)
RABBIT_HOST = os.environ.get('RABBIT_HOST', 'localhost')
RABBIT_USER = os.environ.get('RABBIT_USER', 'guest')
RABBIT_PASS = os.environ.get('RABBIT_PASS', 'guest')
# BROKER_URL = 'redis://{}:{}/{}'.format(REDIS_HOST, REDIS_PORT, REDIS_DB)
BROKER_URL = 'amqp://{}:{}@{}:{}//'.format(
    RABBIT_USER, RABBIT_PASS, RABBIT_HOST, RABBIT_PORT)
# CELERY_RESULT_BACKEND = 'redis://{}:{}/{}'.format(REDIS_HOST, REDIS_PORT, REDIS_DB)

CELERY_TIMEZONE = 'UTC'
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']  # Ignore other content
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ENABLE_UTC = True
CUCUMBER_ROUTE_QUEUE = 'mail'
CELERY_ROUTES = {
    'watcher.tasks.get_screenshot': {'queue': SCREENSHOT_QUEUE},
    'watcher.tasks.check_url_day': {'queue': 'day'},
    'seacucumber.tasks.SendEmailTask': {'queue': CUCUMBER_ROUTE_QUEUE},
}
CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"
CELERY_IMPORTS = ('seacucumber.tasks',)

API_TOKEN = "**redacted**"


djcelery.setup_loader()
