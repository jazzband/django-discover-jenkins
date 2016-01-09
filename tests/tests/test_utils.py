import os

import discover_jenkins
import test_project
from django.test import TestCase


class TestUtils(TestCase):

    def test_app_locations(self):
        """
        The app locations should come from the test_project settings.
        """
        locations = [os.path.dirname(discover_jenkins.__file__),
                     os.path.dirname(test_project.test_app.__file__)]
        self.assertEqual(discover_jenkins.utils.get_app_locations(),
                         locations)
