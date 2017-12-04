"""
Validate javascript files.

Options:

    * config_file      : str, None, jshint configuration file
    * reporter         : str, None, custom reporter
    * ignore_files     : list, [],  excludes files matching pattern
    * ignore_list_file : str, None, jshintignore file

Requirements:

    * node.js
    * jshint
      to install, run `node install --save-dev jshint`

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
        bld = self.group.context
        cfg = self.conf
        args = self.args

        # Custom configuration file
        if cfg.get('config_file', None):
            args.append("--config='%s'" % bld.path.find_resource(
                cfg['config_file']).abspath())

        # Custom reporter (<PATH>|jslint|checkstyle)
        if cfg.get('reporter', None):
            args.append('--reporter=%s' % cfg['reporter'])

        # Exclude files matching the given filename pattern
        # (same as .jshintignore)
        exclude_files = make_list(cfg.get('ignore_files'))
        for exclude_file in exclude_files:
            args.append('--exclude=%s' % exclude_file)

        # Pass in custom jshintignore file path
        if cfg.get('ignore_list_file', None):
            args.append("--exclude-path='%s'" % bld.path.find_resource(
                cfg['ignore_list_file']).abspath())


    def perform(self):
        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg} {in_}'.format(
            exe=executable,
            arg=' '.join(self.args),
            in_=' '.join(self.file_in),
        ))


def configure(conf):
    bin_path = 'node_modules/jshint/bin/jshint'
    conf.start_msg("Checking for program '%s'" % tool_name)
    if os.path.exists(bin_path):
        bin_path = os.path.realpath(bin_path)
        conf.end_msg(bin_path)
    else:
        conf.end_msg('not found', color='YELLOW')
        bin_path = conf.find_program('jshint')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
