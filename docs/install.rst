.. ref-install:

Installation
============

From PyPI::

    pip install django-discover-jenkins

Due to a bug in the coverage library you have to use this specific version::

    pip install coverage==3.5

Configuration
-------------

Add ``discover_jenkins`` to your ``INSTALLED_APPS`` and set ``TEST_RUNNER`` to
the ``DiscoverCIRunner`` that ``discover_jenkins`` provides::

    INSTALLED_APPS = (
        ...
        'discover_jenkins',
        ...
    )

    TEST_RUNNER = 'discover_jenkins.runner.DiscoverCIRunner'

Even though ``discover_jenkins`` doesn't use app names to discover tests, it
does use them to handle tasks like coverage and pylint. Add your desired apps
to setting called ``TEST_PROJECT_APPS``::

    TEST_PROJECT_APPS = (
        'my_project.my_app',
        'my_project.my_other_app',
    )

Usage
-----

Run Django's ``test`` management command with the ``--jenkins`` option::

    python manage.py test --jenkins

If you have not specified a different directory, the output will go to a
directory called "reports" under your current working directory. You can use
this output in Jenkins to measure your results.
