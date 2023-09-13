"""
Django settings for EatUp project.

Generated by 'django-admin startproject' using Django 4.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import datetime
import os.path
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
import sys
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-56wy+gfr%-80tw)b0a_vb9$@prsfp@kaxj#$an12rlk77kam*r'
# SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',
    'customerapp.apps.CustomerappConfig',
    'riderapp.apps.RiderappConfig',
    'vendorapp.apps.VendorappConfig',
    'phonenumber_field',
    'rest_framework',
    'django_nose',
    'corsheaders',
    # "push_notifications",
    # 'rest_framework_simplejwt.token_blacklist',
    # documentation
    'drf_spectacular',
    # location
    'django.contrib.gis',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware'
]

ROOT_URLCONF = 'EatUp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'EatUp.wsgi.application'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


# settings.py
# if 'test' in sys.argv:
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': ':memory:',
#         }
#     }
# else:
if os.getcwd() == '/app':
    DATABASES = {'default': dj_database_url.config(default=os.environ['DATABASE_URL'], engine='django.contrib.gis.db.backends.postgis')}
    GDAL_LIBRARY_PATH = None
    GEOS_LIBRARY_PATH = None
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'EatUp',
            'USER': 'postgres',
            'PASSWORD': 'Oreoluwa',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        },
        'default_': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite',
        },
        'default1': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'EatUp',
            'USER': 'postgres',
            'PASSWORD': '',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        },
    }
    # GDAL_LIBRARY_PATH = None
    # GEOS_LIBRARY_PATH = None
    GDAL_LIBRARY_PATH = '/opt/homebrew/lib/libgdal.dylib'
    GEOS_LIBRARY_PATH = '/opt/homebrew/lib/libgeos_c.dylib'
# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Custom user model
AUTH_USER_MODEL = "users.User"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 10,
    'NON_FIELD_ERRORS_KEY': 'error',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'EatUp Endpoints',
    'DESCRIPTION': 'Endpoints to be consumed by EatUp',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # OTHER SETTINGS
}



SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=5),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    # 'AUTH_HEADER_TYPES': ('Bearer', 'JWT'),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': datetime.timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': datetime.timedelta(days=1),
}


PHONENUMBER_DEFAULT_REGION = 'NG'


# DAPHNE WEBSOCKETS
ASGI_APPLICATION = "EatUp.asgi.application"
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_URL = os.environ.get('REDIS_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}')
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        # "BACKEND": "channels_redis.pubsub.RedisPubSubChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_SEND_EVENTS = True
CELERY_TRACK_STARTED = True

# NOTIFICATIONS
# PUSH_NOTIFICATIONS_SETTINGS = {
#         "FCM_API_KEY": "[your api key]",
#         "GCM_API_KEY": "[your api key]",
#         "APNS_CERTIFICATE": "/path/to/your/certificate.pem",
#         "APNS_TOPIC": "com.example.push_test",
#         "WNS_PACKAGE_SECURITY_ID": "[your package security id, e.g: 'ms-app://e-3-4-6234...']",
#         "WNS_SECRET_KEY": "[your app secret key, e.g.: 'KDiejnLKDUWodsjmewuSZkk']",
#         "WP_PRIVATE_KEY": "/path/to/your/private.pem",
#         "WP_CLAIMS": {'sub': "mailto: development@example.com"}
# }

FIXTURE_DIRS = BASE_DIR

KORAPAY_SECRET_KEY = os.getenv('KORAPAY_SECRET_KEY')
KORAPAY_PUBLIC_KEY = os.getenv('KORAPAY_PUBLIC_KEY')
KORAPAY_ENCRYPTION_KEY = os.getenv('KORAPAY_ENCRYPTION_KEY')
KORAPAY_BASE_URL = 'https://api.korapay.com/merchant/api/v1/'
KORAPAY_DISBURSE_API = KORAPAY_BASE_URL + 'transactions/disburse'
KORAPAY_RESOLVE_API = KORAPAY_BASE_URL + 'misc/banks/resolve'
KORAPAY_AVAILABLE_BANKS_API = KORAPAY_BASE_URL + 'misc/banks'
KORAPAY_CHARGE_API = KORAPAY_BASE_URL + 'charges/initialize'


BASE_URL = 'https://food-delivery-service.herokuapp.com'


TERMII_API_KEY = os.getenv('TERMII_API_KEY')
TERMII_SECRET_KEY = os.getenv('TERMII_SECRET_KEY')

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = ['https://*.herokuapp.com/', 'https://*.127.0.0.1']


DEFAULT_FILE_STORAGE = 'EatUp.storage.FileSystemOverwriteStorage'


DELIVERY_FEE_PER_KM = 500
