# -*- coding: utf-8 -*-
import os
import sys
from optparse import make_option

from discover_jenkins.utils import check_output, get_app_locations


class SlocCountTask(object):
    option_list = (
        make_option(
            "--sloccount-with-migrations",
            action="store_true",
            default=False,
            dest="sloccount_with_migrations",
            help="Count migrations sloc."
        ),
        make_option(
            '--sloccount-stdout',
            action='store_true',
            dest='sloccount_stdout',
            default=False,
            help='Print the sloccount totals instead of saving them to a file'
        ),
    )

    def __init__(self, **options):
        self.with_migrations = options['sloccount_with_migrations']

        if options['sloccount_stdout']:
            self.output = sys.stdout
        else:
            output_dir = options['output_dir']
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            self.output = open(os.path.join(output_dir,
                                            'sloccount.report'), 'w')

    def teardown_test_environment(self, **kwargs):
        locations = get_app_locations()

        report_output = check_output(
            ['sloccount', "--duplicates", "--wide", "--details"] + locations
        )
        report_output = report_output.decode('utf-8')

        if self.with_migrations:
            self.output.write(report_output.decode('utf-8'))
        else:
            for line in report_output.splitlines():
                if '/migrations/' in line:
                    continue
                self.output.write(line)
                self.output.write('\n')
