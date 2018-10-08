"""
Django settings for standalone project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = 'DEBUG' in os.environ

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(', ')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'social_django',
    'simplestats',
    'simplestats.standalone',
    'simplestats.prometheus',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'standalone.urls'
SOCIAL_AUTH_RAISE_EXCEPTIONS = DEBUG

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

WSGI_APPLICATION = 'simplestats.standalone.wsgi.application'
ROOT_URLCONF = 'simplestats.standalone.urls'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {'default': dj_database_url.config(
    env='DATABASE_URL',
    default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
)}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('STATIC_ROOT')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get('MEDIA_ROOT')

# Enable Sentry
if 'SENTRY_DSN' in os.environ:
    # Set your DSN value
    RAVEN_CONFIG = {'dsn': os.environ.get('SENTRY_DSN')}
    INSTALLED_APPS += ('raven.contrib.django.raven_compat',)

# See documentation here
# http://psa.matiasaguirre.net/docs/backends/google.html?highlight=google
SOCIAL_AUTH_RAISE_EXCEPTIONS = DEBUG
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GooglePlusAuth',
    'django.contrib.auth.backends.ModelBackend',
)
SOCIAL_AUTH_GOOGLE_PLUS_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_PLUS_KEY')
SOCIAL_AUTH_GOOGLE_PLUS_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_PLUS_SECRET')
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'

TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
TEST_OUTPUT_VERBOSE = 2
TEST_OUTPUT_DIR = 'test-results'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
}
