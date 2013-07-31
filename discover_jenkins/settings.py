from django.conf import settings

DEFAULT_OUTPUT_DIR = "reports"
DEFAULT_TASKS = (
    'django_jenkins.tasks.run_pylint',
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.django_tests',
)

TASKS = getattr(settings, 'TEST_JENKINS_TASKS', DEFAULT_TASKS)
OUTPUT_DIR = getattr(settings, 'TEST_JENKINS_OUTPUT_DIR', DEFAULT_OUTPUT_DIR)
