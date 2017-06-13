#coding:utf-8
"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from mongoengine import connect

MONGODB_DBNAME = 'test'
connect(MONGODB_DBNAME)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_DIR = os.path.dirname(__file__)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$gij!o80ffhyv8shq@4na7@^g^=(05e5e$y!ji$8000y@nnib!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gallery',
]
SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'gallery/template'),
            os.path.join(BASE_DIR, 'mysite/template'),
        ],
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

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': ('instagram_test'),
        'USER': ('root'),
        'PASSWORD': ('1234'),
        'HOST': ('127.0.0.1'),
        'POST': 3306,
    },

    'mongo': {
        'ENGINE': 'django.db.backends.dummy',
    }
}

# session cookie
SESSION_COOKIE_NAME = 'exe_iis_session_id'
SESSION_COOKIE_HTTPONLY = False

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

AUTH_PROFILE_MODULE = 'mysite.UserProfile'

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Setup support for proxy headers
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
    'C:\\instagram_images',
    'C:\\Python27_x86\\Scripts\\scrapy_instagram\\images',
    '/home/images/',    
)

IMAGES_DIR = '/instagram_images/'

EXTERNAL_INDEX_URL = 'http://127.0.0.1:8000/static/index.html'
INTERNAL_LOGIN_URL = 'http://127.0.0.1:8000/accounts/login/'

IMAGES_PER_PAGE = 20
APPEND_SLASH = False

LOGO_IMG_NAME = 'exe.png'

#Login error messages
ERROR_USERNAME_NOT_EXIST = '*该用户不存在'
ERROR_PHONE_NOT_EXIST = '*手机号不存在'
ERROR_WRONG_PASSWORD = '*密码错误,请重新输入'

#Register error messages
ERROR_FORM_INVALID = '*表单信息错误'
ERROR_PASSWORD_NOT_IDENTICAL = '*密码不一致，请重新输入'
ERROR_USERNAME_TAKEN = '*该用户名已被使用'
ERROR_PHONE_TAKEN = '*该手机号已被使用'