import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ROOT_URLCONF = 'test_app.urls'
SECRET_KEY = 'nokey'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEST_PROJECT_APPS = (
    'discover_jenkins',
    'test_project.test_app',
)

INSTALLED_APPS = (
    'django.contrib.contenttypes',
) + TEST_PROJECT_APPS


DATABASE_ENGINE = 'sqlite3'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.%s' % DATABASE_ENGINE,
    }
}

TEST_RUNNER = 'discover_jenkins.runner.DiscoverCIRunner'
TEST_TASKS = (
    'discover_jenkins.tasks.with_coverage.CoverageTask',
    'discover_jenkins.tasks.run_pylint.PyLintTask',
    'discover_jenkins.tasks.run_flake8.Flake8Task',
    'discover_jenkins.tasks.run_jshint.JSHintTask',
    'discover_jenkins.tasks.run_sloccount.SlocCountTask',
)

JSHINT_CHECKED_FILES = [os.path.join(BASE_DIR, 'project/static/js/test.js')]


STATIC_URL = '/static/'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
