"""
Django settings for docServer project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

ADMINS = (
    ('Ioannis Oikonomidis', 'johnnyecon@gmail.com'),
)

MANAGERS = (
    ('Ioannis Oikonomidis', 'johnnyecon@gmail.com'),
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'j(7=phd10!ldysr&f($0x^g*8_-7hv!-&e0l@sel0#vcgu7#_a'

# Application definition

TEMPLATE_CONTEXT_PROCESSORS = (
    'pinax_theme_bootstrap.context_processors.theme',
    'django.core.context_processors.static',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'account.context_processors.account',
    'django.core.context_processors.request',
    'context_processors.debug_mode'
)
LOGIN_REDIRECT_URL = '/account/login'
LOGIN_URL = '/account/login'
LOGOUT_URL = '/account/login'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'docServer',
    'pinax_theme_bootstrap',
    'bootstrapform',
    'account',
    'bootstrap_pagination',
    'storages',
    'require',
    'django_behave',
    'bdd_tests',
    'rest_framework',
    'rest_framework.authtoken',
    'ajaxuploader',
    'session_security',
    'redis_cache',
    'report_builder'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'account.middleware.LocaleMiddleware',
    'account.middleware.TimezoneMiddleware',
    'session_security.middleware.SessionSecurityMiddleware',
)

SESSION_COOKIE_AGE = 60 * 60
SESSION_SECURITY_WARN_AFTER = 50 * 60
SESSION_SECURITY_EXPIRE_AFTER = 60 * 60
# SESSION_SECURITY_WARN_AFTER = 1 * 5
# SESSION_SECURITY_EXPIRE_AFTER = 1 * 10

ROOT_URLCONF = 'docServer.urls'

WSGI_APPLICATION = 'docServer.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Copenhagen'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'pinax_theme_bootstrap', 'templates'),
    os.path.join(BASE_DIR, 'docServer', 'templates'),
)

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 's')
STATICFILES_STORAGE = 'require.storage.OptimizedStaticFilesStorage'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
REQUIRE_BUILD_PROFILE = "app.build.js"
REQUIRE_BASE_URL = "js/"
REQUIRE_STANDALONE_MODULES = {
# #     "main": {
# #         "out": "main.build.js"
# #     },
# #     "modals": {
# #         "out": "modals.build.js"
# #     },
#     "project": {
#         "out": "project-app.build.js",
#         "build_profile": "project-app.build.js",
#     },
}

TEST_RUNNER = 'django_behave.runner.DjangoBehaveTestSuiteRunner'

REPORT_BUILDER_GLOBAL_EXPORT = True

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}