import inspect

from optparse import make_option

from django.core.exceptions import ImproperlyConfigured
from django.utils import unittest
from django.utils.importlib import import_module

try:
    # Django 1.6
    from django.test.runner import DiscoverRunner
except ImportError:
    # Fallback to third-party app on Django 1.5
    from discover_runner.runner import DiscoverRunner

from .results import XMLTestResult
from .settings import TASKS, OUTPUT_DIR


def get_tasks():
    """Get the imported task classes for each task that will be run"""
    task_classes = []
    for task_path in TASKS:
        try:
            module, classname = task_path.rsplit('.', 1)
        except ValueError:
            raise ImproperlyConfigured('%s isn\'t a task module' % task_path)
        try:
            mod = import_module(module)
        except ImportError as e:
            raise ImproperlyConfigured('Error importing task %s: "%s"'
                                       % (module, e))
        try:
            task_class = getattr(mod, classname)
        except AttributeError:
            raise ImproperlyConfigured('Task module "%s" does not define a '
                                       '"%s" class' % (module, classname))
        task_classes.append(task_class)
    return task_classes


def get_task_options():
    """Get the options for each task that will be run"""
    options = ()

    task_classes = get_tasks()
    for cls in task_classes:
        options += cls.option_list

    return options


class CIRunner(object):
    """
    A Django test runner mixin that runs tasks for Jenkins and dumps the
    results to an XML file.
    """
    option_list = get_task_options() + (
        make_option(
            '--jenkins',
            action='store_true',
            dest='jenkins',
            default=False,
            help='Process the Jenkins tasks from TEST_JENKINS_TASKS.'
        ),
        make_option(
            '--output-dir',
            action='store',
            dest='output_dir',
            default=OUTPUT_DIR,
            help='Top level of project for unittest discovery.'
        ),
    )

    def __init__(self, jenkins=False, output_dir=None, **options):
        super(CIRunner, self).__init__(**options)
        self.jenkins = jenkins

        if self.jenkins:
            self.output_dir = output_dir

            # Import each requested task
            task_classes = get_tasks()

            # Instantiate the tasks
            self.tasks = []
            for task_class in task_classes:
                instance = task_class(output_dir=output_dir, **options)
                self.tasks.append(instance)

    def setup_test_environment(self, **kwargs):
        super(CIRunner, self).setup_test_environment(**kwargs)
        if self.jenkins:
            for task in self.tasks:
                if hasattr(task, 'setup_test_environment'):
                    task.setup_test_environment(**kwargs)

    def run_suite(self, suite, **kwargs):
        if self.jenkins:
            for task in self.tasks:
                if hasattr(task, 'before_suite_run'):
                    task.before_suite_run(suite, **kwargs)

            # Use the XMLTestResult so that results can be saved as XML
            result = unittest.TextTestRunner(
                buffer=True,
                resultclass=XMLTestResult,
                verbosity=self.verbosity,
                failfast=self.failfast,
            ).run(suite)

            # Dump the results to an XML file
            result.dump_xml(self.output_dir)

            for task in self.tasks:
                if hasattr(task, 'after_suite_run'):
                    task.after_suite_run(suite, **kwargs)

            return result
        # If Jenkins is not enabled, just run the suite as normal
        return super(CIRunner, self).run_suite(suite, **kwargs)

    def teardown_test_environment(self, **kwargs):
        super(CIRunner, self).teardown_test_environment(**kwargs)
        if self.jenkins:
            for task in self.tasks:
                if hasattr(task, 'teardown_test_environment'):
                    task.teardown_test_environment(**kwargs)


class DiscoverCIRunner(CIRunner, DiscoverRunner):
    """The CIRunner mixin applied to the discover runner"""
    option_list = DiscoverRunner.option_list + CIRunner.option_list
