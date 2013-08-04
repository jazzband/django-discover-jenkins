# -*- coding: utf-8 -*-
# pylint: disable=W0201
import os
import sys
from optparse import make_option

from pylint import lint
from pylint.reporters.text import ParseableTextReporter

from ..settings import PYLINT_RCFILE, PROJECT_APPS


def default_config_path():
    rcfile = PYLINT_RCFILE
    if os.path.exists(rcfile):
        return rcfile

    # use build-in
    root_dir = os.path.normpath(os.path.dirname(__file__))
    return os.path.join(root_dir, 'pylint.rc')


class PyLintTask(object):
    option_list = (
        make_option(
            "--pylint-rcfile",
            dest="pylint_rcfile",
            default=None,
            help="pylint configuration file"
        ),
        make_option(
            "--pylint-errors-only",
            dest="pylint_errors_only",
            action="store_true",
            default=False,
            help="pylint output errors only mode"
        ),
    )

    def __init__(self, **options):
        self.config_path = options['pylint_rcfile'] or default_config_path()
        self.errors_only = options['pylint_errors_only']

        if options.get('pylint_file_output', True):
            output_dir = options['output_dir']
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            self.output = open(os.path.join(output_dir, 'pylint.report'), 'w')
        else:
            self.output = sys.stdout

    def teardown_test_environment(self, **kwargs):
        if PROJECT_APPS:
            args = ["--rcfile=%s" % self.config_path]
            if self.errors_only:
                args += ['--errors-only']
            args += PROJECT_APPS

            lint.Run(args, reporter=ParseableTextReporter(output=self.output),
                                                          exit=False)
