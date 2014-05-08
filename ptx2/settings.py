"""
Django settings for ptx2 project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import dj_database_url  # add this to requirements.txt
DATABASES = {  
    'default': {  
        'ENGINE': 'django.db.backends.postgresql_psycopg2', 
        'NAME': 'ptonptx2',                      # Or path to database file if using sqlite3.  
        'USER': 'admin',                      # Not used with sqlite3.  
        'PASSWORD': 'password',                  # Not used with sqlite3.  
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.  
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.  
    }  
} 

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, 'ptx2app/templates/ptonptx2')

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    TEMPLATE_PATH,
)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'f+n&gf!ph09l@9w=vy5%^@zl8lf4bzc12^#d(^s*5bhcou&xub'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = []

#email
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'princetonptx2@gmail.com'
EMAIL_HOST_PASSWORD = 'ptonptx2'

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ptx2app',
    'south'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_cas.middleware.CASMiddleware',
)

#CAS stuff
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas.backends.CASBackend',
)
CAS_SERVER_URL = 'https://fed.princeton.edu/cas/'

ROOT_URLCONF = 'ptx2.urls'

WSGI_APPLICATION = 'ptx2.wsgi.application'

AUTH_PROFILE_MODULE = 'ptx2app.Profile'

TEMPLATE_CONTEXT_PROCESSORS = (
   "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",

	"ptx2.context_processors.baseurl"
)


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

try:
	HOSTNAME = socket.gethostname()
except:
	HOSTNAME = 'localhost'



import dj_database_url

dbconfig = dj_database_url.config()
if dbconfig:
    DATABASES['default'] =  dbconfig

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static asset configuration
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
