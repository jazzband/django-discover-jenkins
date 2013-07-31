import inspect

from optparse import make_option

from django.utils import unittest
from django.utils.importlib import import_module

try:
    # Django 1.6
    from django.test.runner import DiscoverRunner
except ImportError:
    # Fallback to third-party app on Django 1.5
    from discover_runner.runner import DiscoverRunner

from . import signals
from .results import XMLTestResult
from .settings import TASKS, OUTPUT_DIR


def get_task_options():
    """Get the options for each task that will be run"""
    options = ()

    task_classes = [import_module(module_name).Task for module_name in TASKS]
    for cls in task_classes:
        options += cls.option_list

    return options


class DiscoverCIRunner(DiscoverRunner):
    """
    A Django test runner that runs tasks for Jenkins and dumps the results to
    an XML file.
    """
    option_list = DiscoverRunner.option_list + get_task_options() + (
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
        super(DiscoverCIRunner, self).__init__(**options)
        self.jenkins = jenkins

        if self.jenkins:
            self.output_dir = output_dir

            # Import each requested task
            task_classes = [import_module(module_name).Task
                            for module_name in TASKS]

            # Instantiate the tasks
            self.tasks = []
            for cls in task_classes:
                instance = cls(output_dir=output_dir, **options)
                self.tasks.append(instance)

            # Connect the signals to the listeners for each task that should be
            # run.
            for signal_name, signal in inspect.getmembers(signals,
                                                    predicate=lambda obj: obj):
                for task in self.tasks:
                    signal_handler = getattr(task, signal_name, None)
                    if signal_handler:
                        signal.connect(signal_handler)

    def setup_test_environment(self, **kwargs):
        super(DiscoverCIRunner, self).setup_test_environment(**kwargs)
        if self.jenkins:
            signals.setup_test_environment.send(sender=self)

    def run_suite(self, suite, **kwargs):
        if self.jenkins:
            signals.before_suite_run.send(sender=self)

            # Use the XMLTestResult so that results can be saved as XML
            result = unittest.TextTestRunner(
                buffer=True,
                resultclass=XMLTestResult,
                verbosity=self.verbosity,
                failfast=self.failfast,
            ).run(suite)

            # Dump the results to an XML file
            result.dump_xml(self.output_dir)

            signals.after_suite_run.send(sender=self)

            return result
        return super(DiscoverCIRunner, self).run_suite(suite, **kwargs)

    def teardown_test_environment(self, **kwargs):
        super(DiscoverCIRunner, self).teardown_test_environment(**kwargs)
        if self.jenkins:
            signals.teardown_test_environment.send(sender=self)
