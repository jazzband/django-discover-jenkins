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


class DiscoverCIRunner(DiscoverRunner):
    """
    A Django test runner that runs tasks for Jenkins and dumps the results to
    an XML file.
    """
    option_list = DiscoverRunner.option_list + (
        make_option('--jenkins',
            action='store_true', dest='jenkins', default=False,
            help='Process the Jenkins tasks from TEST_JENKINS_TASKS.'),
        make_option('--output-dir',
            action='store', dest='output_dir', default=OUTPUT_DIR,
            help='Top level of project for unittest discovery.'),
    )

    def __init__(self, jenkins=False, output_dir=None, **kwargs):
        super(DiscoverCIRunner, self).__init__(**kwargs)
        self.jenkins = jenkins

        if jenkins:
            self.output_dir = output_dir

            # Import each requested task
            self.tasks_cls = [import_module(module_name).Task
                              for module_name in TASKS]

    def setup_test_environment(self, **kwargs):
        super(DiscoverCIRunner, self).setup_test_environment()
        if self.jenkins:
            signals.setup_test_environment.send(sender=self)

    def build_suite(self, *args, **kwargs):
        suite = super(DiscoverCIRunner, self).build_suite(*args, **kwargs)
        if self.jenkins:
            signals.build_suite.send(sender=self, suite=suite)
        return suite

    def teardown_test_environment(self, **kwargs):
        super(DiscoverCIRunner, self).teardown_test_environment()
        if self.jenkins:
            signals.teardown_test_environment.send(sender=self)

    def run_suite(self, suite, **kwargs):
        if self.jenkins:
            # Instantiate the tasks
            self.tasks = self.get_tasks(suite, output_dir=self.output_dir)

            # Connect the signals to the listeners for each task that should be
            # run.
            for signal_name, signal in inspect.getmembers(signals,
                                                    predicate=lambda obj: obj):
                for task in self.tasks:
                    signal_handler = getattr(task, signal_name, None)
                    if signal_handler:
                        signal.connect(signal_handler)

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

    def get_tasks(self, *test_labels, **options):
        """Instantiate all task instances"""
        return [task_cls(test_labels, options) for task_cls in self.tasks_cls]
