"""
Browserify lets you require('modules') in the browser by bundling up all of
your dependencies.

This tool will accept multiple file_in, but only the first one will be
processed, the others are treated as dependency.

Options:

    * transform_module: list, [], use a transform module on
                        top-level files

Requirements:

    * node.js
    * browserify
      to install, run `npm install --save-dev browserify`

"""

import os
from pybuildtool import BaseTask, make_list

tool_name = __name__

class Task(BaseTask):

    conf = {
        '_source_grouped_': True,
    }
    name = tool_name

    def prepare(self):
        args = self.args
        conf = self.conf

        for mod in make_list(conf.get('transform_module')):
            args.append("--transform '%s'" % mod)


    def perform(self):
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
    bin_path = 'node_modules/browserify/bin/cmd.js'
    conf.start_msg("Checking for program '%s'" % tool_name)
    if os.path.exists(bin_path):
        bin_path = os.path.realpath(bin_path)
        conf.end_msg(bin_path)
    else:
        conf.end_msg('not found', color='YELLOW')
        bin_path = conf.find_program('browserify')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
