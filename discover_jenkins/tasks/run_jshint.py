# -*- coding: utf-8 -*-
import codecs
import fnmatch
import os
import subprocess
import sys
from optparse import make_option

import django
from django.conf import settings as django_settings

from ..settings import JSHINT_CHECKED_FILES, JSHINT_EXCLUDE, JSHINT_RCFILE
from ..utils import CalledProcessError, get_app_locations


class JSHintTask(object):

    if django.VERSION < (1, 8):
        option_list = (
            make_option(
                "--jshint-no-staticdirs",
                dest="jshint-no-staticdirs",
                default=False,
                action="store_true",
                help="Don't check js files located in STATICFILES_DIRS settings"
            ),
            make_option(
                "--jshint-with-minjs",
                dest="jshint_with-minjs",
                default=False,
                action="store_true",
                help="Do not ignore .min.js files"
            ),
            make_option(
                "--jshint-exclude",
                dest="jshint_exclude",
                default=JSHINT_EXCLUDE,
                help="Exclude patterns"
            ),
            make_option(
                '--jshint-stdout',
                action='store_true',
                dest='jshint_stdout',
                default=False,
                help='Print the jshint output instead of storing it in a file'
            ),
            make_option(
                '--jshint-rcfile',
                dest='jshint_rcfile',
                default=JSHINT_RCFILE,
                help='Provide an rcfile for jshint'
            ),
        )

    def __init__(self, **options):
        self.to_stdout = options['jshint_stdout']
        self.no_static_dirs = options['jshint-no-staticdirs']
        self.jshint_with_minjs = options['jshint_with-minjs']
        self.jshint_rcfile = options['jshint_rcfile']

        if self.to_stdout:
            self.output = sys.stdout
        else:
            output_dir = options['output_dir']
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            self.output = codecs.open(os.path.join(output_dir,
                                                   'jshint.xml'), 'w', 'utf-8')

        self.exclude = options['jshint_exclude']
        if isinstance(self.exclude, str):
            self.exclude = self.exclude.split(',')

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("--jshint-no-staticdirs",
            dest="jshint-no-staticdirs", default=False, action="store_true",
            help="Don't check js files located in STATICFILES_DIRS settings")
        parser.add_argument("--jshint-with-minjs",
            dest="jshint_with-minjs", default=False, action="store_true",
            help="Do not ignore .min.js files")
        parser.add_argument("--jshint-exclude",
            dest="jshint_exclude", default=JSHINT_EXCLUDE,
            help="Exclude patterns")
        parser.add_argument('--jshint-stdout',
            action='store_true', dest='jshint_stdout', default=False,
            help='Print the jshint output instead of storing it in a file')
        parser.add_argument('--jshint-rcfile',
            dest='jshint_rcfile', default=JSHINT_RCFILE,
            help='Provide an rcfile for jshint')

    def teardown_test_environment(self, **kwargs):
        files = [path for path in self.static_files_iterator()]

        cmd = ['jshint']
        if not self.to_stdout:
            cmd += ['--jslint-reporter']
        if self.jshint_rcfile is not None:
            cmd += ['--config=%s' % self.jshint_rcfile]
        cmd += files

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        output, err = process.communicate()
        retcode = process.poll()
        if retcode not in [0, 2]:  # normal jshint return codes
            raise CalledProcessError(retcode, cmd, output='%s\n%s' % (output, err))

        self.output.write(output.decode('utf-8'))

    def static_files_iterator(self):
        locations = get_app_locations()

        def in_tested_locations(path):
            if not self.jshint_with_minjs and path.endswith('.min.js'):
                return False

            for location in list(locations):
                if path.startswith(location):
                    return True
            if not self.no_static_dirs:
                for location in list(django_settings.STATICFILES_DIRS):
                    if path.startswith(location):
                        return True
            return False

        def is_excluded(path):
            for pattern in self.exclude:
                if fnmatch.fnmatchcase(path, pattern):
                    return True
            return False

        if JSHINT_CHECKED_FILES:
            for path in JSHINT_CHECKED_FILES:
                yield path

        if 'django.contrib.staticfiles' in django_settings.INSTALLED_APPS:
            # use django.contrib.staticfiles
            from django.contrib.staticfiles import finders

            for finder in finders.get_finders():
                for path, storage in finder.list(ignore_patterns=None):
                    path = os.path.join(storage.location, path)
                    if path.endswith('.js') and in_tested_locations(path):
                        if not is_excluded(path):
                            yield path
        else:
            # scan apps directories for static folders
            for location in locations:
                for dirpath, dirnames, filenames in \
                        os.walk(os.path.join(location, 'static')):
                    for f in filenames:
                        path = os.path.join(dirpath)
                        if path.endswith('.js') and in_tested_locations(path):
                            if not is_excluded(path):
                                yield path
