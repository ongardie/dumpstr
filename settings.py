# Django settings for dumpstr project.
# Refer to https://docs.djangoproject.com/en/dev/ref/settings/ for
# documentation.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None

ROOT_URLCONF = 'dumpstr.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/home/dumpstr/dumpstr/templates/',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'dumpstr.views.context_processor',
)

INSTALLED_APPS = (
    'dumpstr',
)

# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

# prepended to URLs in the application
# must have trailing and leading slash
WWW_ROOT = '/'

# the trend IDs of trends shown on the home page
HOME_TRENDS = ['test']

try:
    from local_settings import *
except:
    pass
