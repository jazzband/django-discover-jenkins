import os
from datetime import timedelta

from django.test import TestCase

import discover_jenkins
import test_project


class TestUtils(TestCase):

    def test_total_seconds(self):
        """
        The total_seconds util should show that 5 minutes is 300 seconds.
        """
        delta = timedelta(minutes=5)
        self.assertEqual(discover_jenkins.utils.total_seconds(delta), 300)

    def test_app_locations(self):
        """
        The app locations should come from the test_project settings.
        """
        locations = [os.path.dirname(discover_jenkins.__file__),
                     os.path.dirname(test_project.test_app.__file__)]
        self.assertEqual(discover_jenkins.utils.get_app_locations(),
                         locations)
