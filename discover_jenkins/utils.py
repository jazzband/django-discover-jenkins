import os.path
import subprocess
from importlib import import_module

from discover_jenkins.settings import PROJECT_APPS


class CalledProcessError(subprocess.CalledProcessError):
    def __init__(self, returncode, cmd, output=None):
        super(CalledProcessError, self).__init__(returncode, cmd)
        self.output = output

    def __str__(self):
        return ("Command '%s' returned non-zero exit status %d\nOutput:\n%s"
                % (self.cmd, self.returncode, self.output))


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


def get_app_locations():
    """
    Returns list of paths to tested apps
    """
    return [os.path.dirname(os.path.normpath(import_module(app_name).__file__))
            for app_name in PROJECT_APPS]
