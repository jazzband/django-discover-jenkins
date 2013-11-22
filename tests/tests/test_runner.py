from mock import MagicMock, patch
from django.test import TestCase

from discover_jenkins import runner, tasks


class FakeTestRunner(object):
    """
    A fake object to stub out the base methods that the mixin's super() calls
    require.
    """

    def setup_test_environment(self):
        pass

    def teardown_test_environment(self):
        pass


class Runner(runner.CIRunner, FakeTestRunner):
    """CIRunner is a mixin, so use the FakeTestRunner as a base"""
    pass


class TestCIRunner(TestCase):


    def test_get_tasks(self):
        """
        Make sure the correct tasks are imported based on the
        test_project.settings.
        """
        self.assertEqual(runner.get_tasks(),
                         [tasks.with_coverage.CoverageTask,
                          tasks.run_pylint.PyLintTask,
                          tasks.run_flake8.Flake8Task,
                          tasks.run_jshint.JSHintTask,
                          tasks.run_sloccount.SlocCountTask])

    def test_get_task_options(self):
        """
        For now, just do a simple test to make sure the right number of options
        are gleaned from the tasks.
        """
        self.assertEqual(len(runner.get_task_options()), 20)

    def test_setup_test_environment(self):
        """
        Make sure the setup_test_environment method on a task is triggered by
        the runner.
        """
        mock_task = MagicMock()
        with patch.object(Runner, '__init__') as mock_init:
            mock_init.return_value = None
            cirun = Runner()
            cirun.jenkins = True
            cirun.tasks = [mock_task]
            cirun.setup_test_environment()

        self.assertTrue(mock_task.setup_test_environment.called)

    def test_teardown_test_environment(self):
        """
        Make sure the setup_test_environment method on a task is triggered by
        the runner.
        """
        mock_task = MagicMock()
        with patch.object(Runner, '__init__') as mock_init:
            mock_init.return_value = None
            cirun = Runner()
            cirun.jenkins = True
            cirun.tasks = [mock_task]
            cirun.teardown_test_environment()

        self.assertTrue(mock_task.teardown_test_environment.called)

