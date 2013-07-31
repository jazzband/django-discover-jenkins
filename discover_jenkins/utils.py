import os.path
import subprocess

from django.utils.importlib import import_module

from discover_jenkins.settings import PROJECT_APPS


class CalledProcessError(subprocess.CalledProcessError):
    def __init__(self, returncode, cmd, output=None):
        super(CalledProcessError, self).__init__(returncode, cmd)
        self.output = output

    def __str__(self):
        return ("Command '%s' returned non-zero exit status %d\nOutput:\n%s"
                % (self.cmd, self.returncode, self.output))


def check_output(*popenargs, **kwargs):
    """
    Backport from Python2.7
    """
    if getattr(subprocess, 'check_output', None) is None:
        if 'stdout' in kwargs or 'stderr' in kwargs:
            raise ValueError('stdout or stderr argument not allowed, '
                             'it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   *popenargs, **kwargs)
        output, err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise CalledProcessError(retcode, cmd, output=output + '\n' + err)
        return output
    return subprocess.check_output(*popenargs, **kwargs)


def find_first_existing_executable(exe_list):
    """
    Accepts list of [('executable_file_path', 'options')],
    Returns first working executable_file_path
    """
    for filepath, opts in exe_list:
        try:
            proc = subprocess.Popen([filepath, opts],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            proc.communicate()
        except OSError:
            pass
        else:
            return filepath


def total_seconds(delta):
    """
    Backport timedelta.total_seconds() from Python 2.7
    """
    if getattr(delta, 'total_seconds', None) is None:
        return delta.days * 86400.0 + delta.seconds + delta.microseconds * 1e-6
    return delta.total_seconds()


def get_app_locations():
    """
    Returns list of paths to tested apps
    """
    return [os.path.dirname(os.path.normpath(import_module(app_name).__file__))
            for app_name in PROJECT_APPS]
