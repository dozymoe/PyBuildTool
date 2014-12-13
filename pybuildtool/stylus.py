"""
Preprocess CSS files using [Stylus](http://learnboost.github.io/stylus/).

Options:

    * plugins-path  : list, [],    location of stylus plugins
    * inline-image  : bool, False, use data URI
    * includes-path : list, [],    lookup paths
    * compress      : bool, False, compress CSS output
    * firebug       : bool, False, debug information for FireStylus
    * line-numbers  : bool, False, print out stylus line number
    * import-files  : bool, [],    always import selected stylus files
    * include-css   : bool, True,  pull in CSS files with @import
    * resolve-url   : bool, True,  resolve relative urls inside imports

Requirements:

    * stylus
      to install, edit package.json, run `npm install`
    * node.js

"""

import os
from base import Task as BaseTask

tool_name = __name__

class Task(BaseTask):
    conf = {
        'replace_patterns': ((r'\.styl$', '.css'),)
    }

    def prepare_args(self):
        cfg = self.conf
        args = ['--print']

        # Utilize the Stylus plugin at <path>.
        plugin_dirs = cfg.get('plugins-path', [])
        if not isinstance(plugin_dirs, list):
            plugin_dirs = [plugin_dirs]
        for plugin_dir in plugin_dirs:
            args.append('--use=%s' % plugin_dir)

        # Utilize image inlining via data URI support.
        if cfg.get('inline-image', False):
            args.append('--inline')

        # Add <path> to lookup paths.
        include_dirs = cfg.get('includes-path', [])
        if not isinstance(include_dirs, list):
            include_dirs = [include_dirs]
        for include_dir in include_dirs:
            args.append('--include=%s' % include_dir)

        # Compress CSS output.
        if cfg.get('compress', False):
            args.append('--compress')

        # Emits debug infos in the generated CSS that can be used by the
        # FireStylus Firebug plugin.
        if cfg.get('firebug', False):
            args.append('--firebug')

        # Emits comments in the generated CSS indicating the corresponding
        # Stylus line
        if cfg.get('line-numbers', False):
            args.append('--line-numbers')

        # Import stylus <file>.
        import_files = cfg.get('import-files', [])
        if not isinstance(import_files, list):
            import_files = [import_files]
        for import_file in import_files:
            args.append('--import=%s' % import_file)

        # Include regular CSS on @import
        if cfg.get('include-css', True):
            args.append('--include-css')

        # Resolve relative urls inside imports
        if cfg.get('resolve-url', True):
            args.append('--resolve-url')

        return args


    def perform(self):
        if len(self.file_out) != 1:
            self.bld.fatal('%s can only have one output' % tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        cat_executable = self.env['CAT_BIN']
        return self.exec_command(
            '{cat} {in_} | {exe} {arg} > {out}'.format(
            cat=cat_executable,
            exe=executable,
            arg=' '.join(self.prepare_args()),
            in_=' '.join(self.file_in),
            out=self.file_out[0],
        ))


def configure(conf):
    if len(conf.env.CAT_BIN) == 0:
        conf.env.CAT_BIN = conf.find_program('cat')[0]

    bin_path = 'node_modules/stylus/bin/stylus'
    conf.start_msg("Checking for progam '%s'" % tool_name)
    if os.path.exists(bin_path):
        bin_path = os.path.realpath(bin_path)
        conf.end_msg(bin_path)
    else:
        conf.end_msg('not found')
        bin_path = conf.find_program('stylus')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
