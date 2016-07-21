# -*- coding: utf-8 -*-
# pylint: disable=W0201
import os
from optparse import make_option

import django

from .. import settings

try:
    from coverage import coverage
except ImportError:
    from coverage.control import coverage


def default_config_path():
    rcfile = settings.COVERAGE_RCFILE
    if os.path.exists(rcfile):
        return rcfile
    return None


class CoverageTask(object):

    if django.VERSION < (1, 8):
        option_list = (
            make_option(
                "--coverage-rcfile",
                dest="coverage_rcfile",
                default="",
                help="Specify configuration file."
            ),
            make_option(
                "--coverage-html-report",
                dest="coverage_html_report_dir",
                default=settings.COVERAGE_REPORT_HTML_DIR,
                help="Directory to which HTML coverage report should be"
                " written. If not specified, no report is generated."
            ),
            make_option(
                "--coverage-no-branch-measure",
                action="store_false",
                default=settings.COVERAGE_MEASURE_BRANCH,
                dest="coverage_measure_branch",
                help="Don't measure branch coverage."
            ),
            make_option(
                "--coverage-with-migrations",
                action="store_true",
                default=settings.COVERAGE_WITH_MIGRATIONS,
                dest="coverage_with_migrations",
                help="Don't measure migrations coverage."
            ),
            make_option(
                "--coverage-exclude",
                action="append",
                default=settings.COVERAGE_EXCLUDE_PATHS,
                dest="coverage_excludes",
                help="Paths to be excluded from coverage"
            )
        )

    def __init__(self, **options):
        self.output_dir = options['output_dir']
        self.with_migrations = options['coverage_with_migrations']
        self.html_dir = options['coverage_html_report_dir']
        self.branch = options['coverage_measure_branch']

        self.exclude_locations = options['coverage_excludes'] or None

        self.coverage = coverage(
            branch=self.branch,
            source=settings.PROJECT_APPS,
            omit=self.exclude_locations,
            config_file=options.get('coverage_rcfile') or default_config_path()
        )

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("--coverage-rcfile",
            dest="coverage_rcfile", default="",
            help="Specify configuration file.")
        parser.add_argument("--coverage-html-report",
            dest="coverage_html_report_dir", default=settings.COVERAGE_REPORT_HTML_DIR,
            help="Directory to which HTML coverage report should be"
                 " written. If not specified, no report is generated.")
        parser.add_argument("--coverage-no-branch-measure",
            action="store_false", default=settings.COVERAGE_MEASURE_BRANCH,
            dest="coverage_measure_branch",
            help="Don't measure branch coverage.")
        parser.add_argument("--coverage-with-migrations",
            action="store_true", default=settings.COVERAGE_WITH_MIGRATIONS,
            dest="coverage_with_migrations",
            help="Don't measure migrations coverage.")
        parser.add_argument("--coverage-exclude",
            action="append", default=settings.COVERAGE_EXCLUDE_PATHS,
            dest="coverage_excludes",
            help="Paths to be excluded from coverage")

    def setup_test_environment(self, **kwargs):
        self.coverage.start()

    def teardown_test_environment(self, **kwargs):
        self.coverage.stop()

        try:
            self.coverage._harvest_data()
        except AttributeError:
            # coverage._harvest_data was renamed to coverage.get_data in
            # coverage.py 4.0.
            self.coverage.get_data()

        morfs = [filename for filename in self.coverage.data.measured_files()
                 if self.want_file(filename)]

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.coverage.xml_report(
            morfs=morfs,
            outfile=os.path.join(self.output_dir, 'coverage.xml')
        )

        if self.html_dir:
            self.coverage.html_report(
                morfs=morfs,
                directory=self.html_dir
            )

    def want_file(self, filename):
        if not self.with_migrations and '/migrations/' in filename:
            return False

        return True
