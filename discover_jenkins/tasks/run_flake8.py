# coding: utf-8
import os
import sys
import pep8
from flake8.engine import get_style_guide
from optparse import make_option
from discover_jenkins.tasks.run_pep8 import Pep8Task
from discover_jenkins.utils import get_app_locations


class Flake8Task(Pep8Task):
    option_list = Pep8Task.option_list + (
        make_option(
            '--max-complexity',
            dest='max_complexity',
            help='McCabe complexity threshold',
        ),
    )

    def __init__(self, **options):
        super(Flake8Task, self).__init__(**options)

        if options.get('flake8_file_output', True):
            output_dir = options['output_dir']
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            self.output = open(os.path.join(output_dir, 'flake8.report'), 'w')
        else:
            self.output = sys.stdout

        if options['max_complexity']:
            self.pep8_options['max_complexity'] = int(options['max_complexity'])

    def teardown_test_environment(self, **kwargs):
        class JenkinsReport(pep8.BaseReport):
            def error(instance, line_number, offset, text, check):
                code = super(JenkinsReport, instance).error(
                    line_number, offset, text, check,
                )

                if not code:
                    return
                sourceline = instance.line_offset + line_number
                self.output.write(
                    '%s:%s:%s: %s\n' %
                    (instance.filename, sourceline, offset + 1, text),
                )

        flake8style = get_style_guide(
            parse_argv=False,
            config_file=self.pep8_rcfile,
            reporter=JenkinsReport,
            **self.pep8_options)

        # Jenkins pep8 validator requires relative paths
        project_root = os.path.abspath(os.path.dirname(__name__))
        for location in map(lambda x: os.path.relpath(x, project_root), get_app_locations()):
            flake8style.input_dir(location)

        self.output.close()
