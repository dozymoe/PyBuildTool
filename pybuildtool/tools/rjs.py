"""
A command line tool for running JavaScript scripts that use the AMD API for
declaring and using JavaScript modules and regular JavaScript script files.

Options:

    * work_dir     : str, None, change current directory before run
    * config_file  : str, None, r.js build file

Requirements:

    * node.js
    * requirejs
      to install, run `npm install --save-dev requirejs`

"""

import os
from pybuildtool import BaseTask, expand_resource

tool_name = __name__

class Task(BaseTask):

    name = tool_name
    prefix = []

    def prepare(self):
        cfg = self.conf

        # Change current directory
        c = cfg.get('work_dir', None)
        if c:
            self.prefix.append('cd %s;' \
                % expand_resource(self.group, c))

        self.args.append('-o %s' % expand_resource(self.group,
            cfg['config_file']))


    def perform(self):
        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{pre} {exe} {arg}'.format(
            exe=executable,
            pre=' '.join(self.prefix),
            arg=' '.join(self.args),
        ))


def configure(conf):
    bin_path = 'node_modules/requirejs/bin/r.js'
    conf.start_msg("Checking for program '%s'" % tool_name)
    if os.path.exists(bin_path):
        bin_path = os.path.realpath(bin_path)
        conf.end_msg(bin_path)
        conf.env['%s_BIN' % tool_name.upper()] = bin_path
    else:
        conf.end_msg('not found', color='YELLOW')
