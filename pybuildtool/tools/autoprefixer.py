"""
Parse CSS and add vendor prefixes to rules by Can I Use

Options:

    * browsers : str, None, add prefixes for selected browsers
                 Separate browsers by comma. For example, '> 1%, opera 12'.
                 You can set browsers by global usage statistics: '> 1%',
                 or last version: 'last 2 versions'
    * keep     : bool, False, do not remove outdated prefixes

Requirements:

    * node.js
    * autoprefixer
      to install, run `npm install --save-dev autoprefixer`

"""

import os
from pybuildtool import BaseTask

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def prepare(self):
        cfg = self.conf

        # browsers
        c = cfg.get('browsers', None)
        if c:
            self.args.append('--browsers %s' % c)

        # outdated prefix
        c = cfg.get('keep', False)
        if c:
            self.args.append('--no-remove')


    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal('%s only need one input' % tool_name.capitalize())
        if len(self.file_out) != 1:
            self.bld.fatal('%s only have one output' % tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg} {in_} -o {out}'.format(
            exe=executable,
            arg=' '.join(self.args),
            in_=self.file_in[0],
            out=self.file_out[0],
        ))


def configure(conf):
    bin_path = 'node_modules/autoprefixer/autoprefixer'
    conf.start_msg("Checking for program '%s'" % tool_name)
    if os.path.exists(bin_path):
        bin_path = os.path.realpath(bin_path)
        conf.end_msg(bin_path)
    else:
        conf.end_msg('not found', color='YELLOW')
        bin_path = conf.find_program('autoprefixer')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
