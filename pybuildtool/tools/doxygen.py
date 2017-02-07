"""
Generate documentation.

Options:

    * work_dir      : str, None, change current directory
    * config_file   : str, None, doxygen configuration file

Requirements:

    * doxygen
      to install, for example run `apt-get install doxygen`

"""

import os
from pybuildtool.core.task import Task as BaseTask
from pybuildtool.misc.path import expand_resource

tool_name = __name__

class Task(BaseTask):

    name = tool_name
    workdir = '.'

    def prepare(self):
        cfg = self.conf
        args = self.args

        # Change current directory, before running pylint, helps module imports
        c = cfg.get('work_dir', None)
        if c:
            self.workdir = expand_resource(self.group, c)

        # Specify a configuration file
        c = cfg.get('config_file', None)
        if c:
            args.append(expand_resource(self.group, c))


    def perform(self):
        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg}'.format(
            exe=executable,
            arg=' '.join(self.args),
        ), cwd=self.workdir)


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = conf.find_program(tool_name)[0]
