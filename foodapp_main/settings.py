"""
Django settings for foodapp_main project.

Generated by 'django-admin startproject' using Django 4.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
from decouple import config
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)
#linode ubuntu instance ip 139.162.250.110
ALLOWED_HOSTS = ['139.162.250.110', '127.0.0.1', 'hungrybuff.co', 'hungrybuff.co.uk', 'www.hungrybuff.co', 'www.hungrybuff.co.uk']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'qrcode',
    'rest_framework',
    'accounts',
    'vendor',
    'customer',
    'menu',
    'marketplace',
    'django.contrib.gis',
    'order',
    'foodapp_main',
    'restapi',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'foodapp_main.locale_middleware.LocaleMiddleware',
    'order.request_object.RequestObjectMiddleware', #custom middleware created to access the request object in models.py
]

ROOT_URLCONF = 'foodapp_main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.get_vendor',
                'accounts.context_processors.get_user_profile',
                'accounts.context_processors.get_google_api',
                'accounts.context_processors.get_paypal_clientid',
                'marketplace.context_processors.get_cart_counter',
                'marketplace.context_processors.get_cart_amount',
                
            ],
        },
    },
]

WSGI_APPLICATION = 'foodapp_main.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'ENGINE' : 'django.contrib.gis.db.backends.postgis',
        'NAME': config('DBNAME'),
        'USER': config('DBUSER'),
        'PASSWORD': config('DBPASSWORD'),
        'HOST': config('DBHOST'),
        'PORT': config('DBPORT')
    }
}

AUTH_USER_MODEL='accounts.User'

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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR /'static'
STATICFILES_DIRS = [
    'foodapp_main/static'
]

#Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR /'media' 
# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'HungryBuff Team'

GOOGLE_API_KEY = 'AIzaSyD76mTxOlw1ZyW-1aFoAx296dl9ubF4w6o'

if DEBUG == True:
    os.environ['PATH'] = os.path.join(BASE_DIR, 'appenv\Lib\site-packages\osgeo') + ';' + os.environ['PATH']
    os.environ['PROJ_LIB'] = os.path.join(BASE_DIR, 'appenv\Lib\site-packages\osgeo\data\proj') + ';' + os.environ['PATH']
    GDAL_LIBRARY_PATH = os.path.join(BASE_DIR, 'appenv\Lib\site-packages\osgeo\gdal304.dll')
    LOCALE = "en-gb.UTF-8"
    CURRENT_SITE = "http://127.0.0.1:8000"
else:
    LOCALE = "en_GB.utf-8"
    CURRENT_SITE = "https://hungrybuff.co"

PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID')
STRIPE_PUB_KEY = config('STRIPE_PUB_KEY')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')
STRIPE_ENDPOINT_SECRET = config('STRIPE_ENDPOINT_SECRET')
HUNGRYBUFF_FEE = config('HUNGRYBUFF_FEE', cast=float)
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"


LOGGING = {
    'version': 1,                       # the dictConfig format version
    'disable_existing_loggers': False,  # retain the default loggers
    'handlers': {
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'error.log',
            'when': 'midnight', 
            'formatter': 'verbose',
            'backupCount' :10,
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
        },
    },
    'formatters': {
        'verbose': {
            'format': '{asctime} {name} {levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
}