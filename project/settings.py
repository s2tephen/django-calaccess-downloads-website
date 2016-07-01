import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '8++yeqnsqgtb8=%oa0&*oa8$2o*6gh0j-+5o+0kq-uq-ycoo3@'
DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'bakery',
    'calaccess_raw',
    'calaccess_website',
    'storages',
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, ".static")

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

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

WSGI_APPLICATION = 'project.wsgi.application'


#
# Bakery
#

BUILD_DIR = os.path.join(BASE_DIR, '.build')
BAKERY_VIEWS = (
    'calaccess_website.views.VersionArchiveIndex',
    'calaccess_website.views.VersionYearArchiveList',
    'calaccess_website.views.VersionDetail',
    'calaccess_website.views.LatestVersion',
    'calaccess_website.views.RawDataFileList',
    'calaccess_website.views.RawDataFileDetail',
    'calaccess_website.views.CalAccess404View',
)

#
# Archiving
#

CALACCESS_DAT_SOURCE = ''
CALACCESS_STORE_ARCHIVE = True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = os.getenv('aws_storage_bucket_name')
S3_URL = 'https://{}.s3-accelerate.amazonaws.com/'.format(
    AWS_STORAGE_BUCKET_NAME
)
AWS_ACCESS_KEY_ID = os.getenv('aws_access_key_id')
AWS_SECRET_ACCESS_KEY = os.getenv('aws_secret_access_key')
AWS_S3_REGION_NAME = os.getenv('aws_region_name')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('db_name'),
        'USER': os.getenv('db_user'),
        'PASSWORD': os.getenv('db_password'),
        'HOST': os.getenv('rds_host'),
        'PORT': '5432',
    },
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
]


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),
            'maxBytes': 1024*1024*5,  # 5MB
            'backupCount': 0,
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s|%(asctime)s|%(module)s|%(message)s',
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(message)s'
        },
    },
    'loggers': {
        'calaccess_raw.management': {
            'handlers': ['logfile',],
            'level': 'DEBUG',
            'propagate': True,
        },
        'bakery': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

try:
    from settings_local import *  # NOQA
except ImportError:
    pass
