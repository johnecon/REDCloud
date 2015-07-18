import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DEBUG = True
INTERNAL_IPS = ('127.0.0.1','localhost')
TEMPLATE_DEBUG = True
REQUIRE_DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}