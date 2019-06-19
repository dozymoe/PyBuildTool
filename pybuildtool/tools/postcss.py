"""
PostCSS is a tool for transforming styles with JS plugins. These plugins can
lint your CSS, support variables and mixins, transpile future CSS syntax,
inline images, and more.

https://github.com/postcss/postcss


Options:

    * map : str, None
          : Create an external sourcemap

    * no_map : bool, None
             : Disable the default inline sourcemaps

    * verbose : bool, None
              : Be verbose

    * env : str, None
          : A shortcut for setting NODE_ENV

    * include_dotfiles : bool, None
                       : Enables glob to match files/dirs that begin with "."

    * use : list, None
          : List of postcss plugins to use

    * parser : str, None
             : Custom postcss parser

    * stringifier : str, None
                  : Custom postcss stringifier

    * syntax : str, None
             : Custom postcss syntax


Requirements:

    * node.js
    * postcss-cli
      to install, run `npm install --save-dev postcss-cli`

"""

import os
from pybuildtool import BaseTask

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def prepare(self):
        self.add_bool_args('no_map', 'include_dotfiles')

        self.add_path_args('map')

        self.add_list_args_multi('use')

        self.add_str_args('env', 'parser', 'stringifier', 'syntax')


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
    bin_path = 'node_modules/postcss-cli/bin/postcss'
    conf.start_msg("Checking for program '%s'" % tool_name)
    if os.path.exists(bin_path):
        bin_path = os.path.realpath(bin_path)
        conf.end_msg(bin_path)
    else:
        conf.end_msg('not found', color='YELLOW')
        bin_path = conf.find_program('postcss')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
