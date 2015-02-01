"""
Precompile handlebars templates.

Requirements:

    * handlebars
      to install, edit package.json, run `npm install`
    * node.js

"""

import os
from base import Task as BaseTask

tool_name = __name__

class Task(BaseTask):

    conf = {
        'replace_patterns': ((r'\.handlebars$', '.js'),),
    }
    name = tool_name

    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal('%s only need one input' % tool_name.capitalize())
        if len(self.file_out) != 1:
            self.bld.fatal('%s can only have one output' % tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg} {in_} -f {out}'.format(
            exe=executable,
            arg=' '.join(self.args),
            in_=self.file_in[0],
            out=self.file_out[0],
        ))


def configure(conf):
    bin_path = 'node_modules/handlebars/bin/handlebars'
    conf.start_msg("Checking for program '%s'" % tool_name)
    if os.path.exists(bin_path):
        bin_path = os.path.realpath(bin_path)
        conf.end_msg(bin_path)
    else:
        conf.end_msg('not found')
        bin_path = conf.find_program('handlebars')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
