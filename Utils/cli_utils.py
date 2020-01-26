import os
import shutil
import time

import click


class cli_utils():
    """
    this class is of easier cli apps usage.
    """

    def __init__(self, click, is_verbose=False, caller=""):
        self.is_verbose = is_verbose
        self.click = click
        self.caller = caller
        self.output_dirname = None
        self.output_path = None
        self._counter = 0

    def msg(self, message, caller=" ", sevirity='INFO', fg=None):
        click.secho("{:<5}: {:<20} {}".format(sevirity, caller, message))

    def header_1_msg(self, message, caller=" ", sevirity='INFO', fg=None):
        head_bar = '------------------------------------------------------------'
        self.msg(head_bar, caller=caller, sevirity=sevirity, fg='green')
        self.msg(message, caller=caller, sevirity=sevirity, fg='green')
        self.msg(head_bar, caller=caller, sevirity=sevirity, fg='green')

    def warn_msg(self, message, caller=""):
        self.msg(message=message, caller=caller, sevirity='WARN')

    def error_msg(self, message, caller=""):
        self.msg(message=message, caller=caller, sevirity='ERROR', fg='red')

    def verbose(self, message, caller="", sevirity='INFO'):
        if self.is_verbose:
            self.msg(message, caller, sevirity)

    def exit(self, exit_code, sevirity, msg):
        click.echo("\n{:<5}: {}  - exit code:{}".format(sevirity, msg, exit_code))
        exit(exit_code)

    def check_file(self, file, option_param_name=None):
        if not file:
            self.error_msg("{}  is mandatory option.".format(option_param_name))
            return 1

        if os.path.isdir(file):
            self.error_msg("I expected file, but this is directory: '{}'".format(option_param_name, file),
                           caller=self.self.caller)
            return 2

        if not os.path.isfile(file):
            self.error_msg("file does not exist: '{}', '{}'".format(option_param_name, file), caller=self.caller)
            return 3
        else:
            self.verbose("OK - {} exists".format(option_param_name), caller=self.caller)
            return 0

    def make_output_dir(self, dirname="output", with_timestamp=False):
        time_stamp = ""
        if with_timestamp:
            time_stamp = time.strftime("%Y%m%d-%H%M%S")
            self.output_dirname = "{}-{}".format(dirname, time_stamp)
        else:
            self.output_dirname = "{}".format(dirname)
        try:
            ret_val = self.mkdir(self.output_dirname)
            self.verbose("output dir is: '{}'".format(dirname))
            return ret_val
        except:
            self.output_dirname = None
            self.output_path = None
            return ret_val

    def mkdir(self, dirname, raise_error_if_exists=True):
        full_dir_path = os.path.join(dirname)
        if os.path.isdir(full_dir_path) and not raise_error_if_exists:
            self.verbose("FYI - {} alresdy exists.".format(dirname), caller=self.mkdir.__name__)
            return 0
        try:
            rv = os.mkdir(full_dir_path)
            if os.path.isdir(full_dir_path):
                self.verbose("OK - mkdir {}".format(dirname), caller=self.mkdir.__name__)
        except Exception as e:
            self.error_msg("{} {} could not be created - {}".format(self.mkdir.__name__, dirname, e),
                           caller=self.mkdir.__name__)
            return 1
        return 0

    def copy_file(self, source, dest):
        try:
            self.verbose("trying to copy {}  to {}".format(source, dest), caller=self.copy_file.__name__)
            rv = shutil.copy(source, dest)
            self.verbose("OK -  copy {}  to {}".format(source, dest), caller=self.copy_file.__name__)
            self._counter += 1
        except Exception as e:
            self.warn_msg("   copy  {}  to {} : {}".format(source, dest, str(e)), caller=self.copy_file.__name__)

    def delete_file(self, file_name):
        try:
            self.verbose("trying to delete {}  ".format(file_name), caller=self.delete_file.__name__)
            rv = os.remove(file_name)
            self.verbose("OK -  delete {}  to {}".format(file_name), caller=self.delete_file.__name__)
            self._counter += 1
        except Exception as e:
            self.warn_msg("   delete  {}  : {}".format(file_name, str(e)), caller=self.delete_file.__name__)

    def rmtree(self, path):
        try:
            self.verbose("trying to rmtree {}  ".format(path), caller=self.rmtree.__name__)
            shutil.rmtree(path)
            self.verbose("OK -  rmtree {}  ".format(path), caller=self.rmtree.__name__)
        except Exception as e:
            self.warn_msg("   rmtree  {} : {}".format(path, str(e)), caller=self.rmtree.__name__)

    def copyfiles_to_dir(self, source_path, dest_dir, files_list):
        self._counter = 0
        for file_name in files_list:
            full_file_name = os.path.join(source_path, file_name)
            self.copy_file(full_file_name, dest_dir)
        self.verbose("OK - {} {} - {} ".format(source_path, dest_dir, self._counter),
                     caller=self.copyfiles_to_dir.__name__)

    def write_file(self, full_file_name, *args):
        try:
            with open(full_file_name, 'w') as file:
                file.writelines(*args)
                self.verbose("File: {} was written".format(full_file_name), caller=self.write_file.__name__)
        except Exception as e:
            self.exit(1, "ERROR", "{} - Exeption:{} args={}".format(full_file_name, e, args))
