.. ref-tasks

=====
Tasks
=====

CoverageTask
============

``discover_runner.tasks.with_coverage.CoverageTask``

Reports test coverage across your apps. Uses the ``TEST_PROJECT_APPS`` setting.

Settings
--------

* ``TEST_COVERAGE_WITH_MIGRATIONS``

  Measure test coverage in your South migrations.

  Default value::

    TEST_COVERAGE_WITH_MIGRATIONS = False

* ``TEST_COVERAGE_REPORT_HTML_DIR``

  Directory to which HTML coverage report should be written. If not specified,
  no HTML report is generated.

  Default value::

    TEST_COVERAGE_REPORT_HTML_DIR = ''

* ``TEST_COVERAGE_MEASURE_BRANCH``

  Measure branch coverage.

  Default value::

    TEST_COVERAGE_MEASURE_BRANCH = True

* ``TEST_COVERAGE_EXCLUDES``

  Module names to exclude.

  Default value::

    TEST_COVERAGE_EXCLUDES = []

* ``TEST_COVERAGE_EXCLUDES_FOLDERS``

  Extra folders to exclude.

  Default value::

    TEST_COVERAGE_EXCLUDES_FOLDERS = []

* ``TEST_COVERAGE_RCFILE``

  Specify configuration file.

  Default value::

    TEST_COVERAGE_RCFILE = 'coverage.rc'

PyLintTask
==========

``discover_runner.tasks.run_pylint.PyLintTask``

Runs pylint across your apps. Uses the ``TEST_PROJECT_APPS`` setting.

Settings
--------

* ``TEST_PYLINT_RCFILE``

  Specify configuration file.

  Default value::

    TEST_PYLINT_RCFILE = 'pylint.rc'

JSHintTask
==========

``discover_runner.tasks.run_jshint.JSHintTask``

Runs jshint across your apps. Uses the ``TEST_PROJECT_APPS`` setting.

Settings
--------

* ``TEST_JSHINT_CHECKED_FILES``

  If provided, check only the specified files.

  Default value::

    TEST_JSHINT_CHECKED_FILES = None

* ``TEST_JSHINT_RCFILE``

  Specify configuration file.

  Default value::

    TEST_JSHINT_RCFILE = None

* ``TEST_JSHINT_EXCLUDE``

  Python ``fnmatch`` patterns for excluded files.

  Default value::

    TEST_JSHINT_EXCLUDE = []

SlocCountTask
=============

``discover_runner.tasks.run_sloccount.SlocCountTask``

Run sloccount across your apps. Uses the ``TEST_PROJECT_APPS`` setting.
