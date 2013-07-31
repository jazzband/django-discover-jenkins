django-discover-jenkins
=======================

A streamlined fork of django-jenkins designed to work with the default test command and the discover runner.

Why?
----

The original [django-jenkins](https://github.com/kmmbvnr/django-jenkins) project doesn't take advantage of improvements to testing introduced in Django 1.4. A special management command is no longer needed, as test runners themself can add options that are handled by the built-in `test` command.

This project is also designed to take advantage of [django-discover-runner](https://github.com/jezdez/django-discover-runner/), which is the default test runner in Django 1.6. Instead of using a setting to list which apps should be tested, it uses the soon-to-be built-in discovery features of the discover runner.
