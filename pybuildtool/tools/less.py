"""
Less-css is a CSS pre-processor, meaning that it extends the CSS language,
adding features that allow variabels, and mixins, functions and many other
techniques that allow you to make CSS that is more maintainable, themable and
extendable.

Options:

    * keep_line_breaks     : bool, False, keep line breaks

Requirements:

    * node.js
    * less
      to install, run `npm install --save-dev less`

"""

import os
from pybuildtool import BaseTask

tool_name = __name__

class Task(BaseTask):

    conf = {
        '_replace_patterns_': ((r'\.less$', '.css'),)
    }
    name = tool_name

    def prepare(self):
        cfg = self.conf
        args = self.args

        # keep line breaks
        if cfg.get('keep_line_breaks', False):
            args.append('--keep-line-breaks')


    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal('%s only need one input' % tool_name.capitalize())
        if len(self.file_out) != 1:
            self.bld.fatal('%s only have one output' % tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg} {in_} {out}'.format(
            exe=executable,
            arg=' '.join(self.args),
            in_=self.file_in[0],
            out=self.file_out[0],
        ))


def configure(conf):
    bin_path = 'node_modules/less/bin/lessc'
    conf.start_msg("Checking for program '%s'" % tool_name)
    if os.path.exists(bin_path):
        bin_path = os.path.realpath(bin_path)
        conf.end_msg(bin_path)
    else:
        conf.end_msg('not found', color='YELLOW')
        bin_path = conf.find_program('lessc')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
