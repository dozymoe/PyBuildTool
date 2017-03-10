"""
Preprocess CSS files using [Stylus](http://learnboost.github.io/stylus/).

Options:

    * plugins       : list, [],    location of stylus plugins
    * inline_image  : bool, False, use data URI
    * include_paths : list, [],    lookup paths
    * compress      : bool, False, compress CSS output
    * firebug       : bool, False, debug information for FireStylus
    * line_numbers  : bool, False, print out stylus line number
    * import_files  : bool, [],    always import selected stylus files
    * include_css   : bool, True,  pull in CSS files with @import
    * resolve_url   : bool, True,  resolve relative urls inside imports

Requirements:

    * node.js
    * stylus
      to install, run `npm install --save-dev stylus`

"""

import os
from pybuildtool.core.task import Task as BaseTask
from pybuildtool.misc.collections import make_list
from pybuildtool.misc.path import expand_resource

tool_name = __name__

class Task(BaseTask):

    conf = {
        'replace_patterns': ((r'\.styl$', '.css'),)
    }
    name = tool_name

    def prepare(self):
        cfg = self.conf
        self.args = ['--print']
        args = self.args

        # Utilize the Stylus plugins.
        for plugin_dir in make_list(cfg.get('plugins')):
            args.append("--use '%s'" % plugin_dir)

        # Utilize image inlining via data URI support.
        c = cfg.get('inline_image', False)
        if c:
            args.append('--inline')

        # Add <path> to lookup paths.
        for include_dir in make_list(cfg.get('include_paths')):
            args.append("--include '%s'" % expand_resource(self.group,
                    include_dir))

        # Compress CSS output.
        c = cfg.get('compress', False)
        if c:
            args.append('--compress')

        # Emits debug infos in the generated CSS that can be used by the
        # FireStylus Firebug plugin.
        c = cfg.get('firebug', False)
        if c:
            args.append('--firebug')

        # Emits comments in the generated CSS indicating the corresponding
        # Stylus line
        c = cfg.get('line_numbers', False)
        if c:
            args.append('--line-numbers')

        # Import stylus <file>.
        for import_file in make_list(cfg.get('import_files')):
            args.append("--import '%s'" % expand_resource(self.group,
                    import_file))

        # Include regular CSS on @import
        c = cfg.get('include_css', True)
        if c:
            args.append('--include-css')

        # Resolve relative urls inside imports
        c = cfg.get('resolve_url', True)
        if c:
            args.append('--resolve-url')


    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal('%s only need one input' % tool_name.capitalize())
        if len(self.file_out) != 1:
            self.bld.fatal('%s can only have one output' %\
                    tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg} < {in_} > {out}'.format(
            exe=executable,
            arg=' '.join(self.args),
            in_=self.file_in[0],
            out=self.file_out[0],
        ))


def configure(conf):
    bin_path = 'node_modules/stylus/bin/stylus'
    conf.start_msg("Checking for program '%s'" % tool_name)
    if os.path.exists(bin_path):
        bin_path = os.path.realpath(bin_path)
        conf.end_msg(bin_path)
    else:
        conf.end_msg('not found', color='YELLOW')
        bin_path = conf.find_program('stylus')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
