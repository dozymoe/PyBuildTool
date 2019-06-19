"""
A mighty, modern linter that helps you avoid errors and enforce conventions in
your styles.

https://github.com/stylelint/stylelint


Options:

    * config : str, None
             : Path to a specific configuration file (JSON, YAML, or CommonJS),
             : or the name of a module in node_modules that points to one. If
             : no --config argument is provided, stylelint will search for
             : configuration files in the following places, in this order:
             :   - a stylelint property in package.json
             :   - a .stylelintrc file (with or without filename extension:
             :     .json, .yaml, .yml, and .js are available)
             :   - a stylelint.config.js file exporting a JS object
             : The search will begin in the working directory and move up the
             : directory tree until a configuration file is found.

    * config_basedir : str, None
                     : An absolute path to the directory that relative paths
                     : defining "extends" and "plugins" are *relative to*.
                     : Only necessary if these values are relative paths.

    * ignore_path : str, None
                  : Path to a file containing patterns that describe files to
                  : ignore. The path can be absolute or relative to
                  : process.cwd(). By default, stylelint looks for
                  : .stylelintignore in process.cwd().

    * ignore_pattern : str, None
                     : Pattern of files to ignore (in addition to those in
                     : .stylelintignore)

    * syntax : str, None
             : Specify a non-standard syntax. Options: "scss", "sass", "less",
             : "sugarss".
             : If you do not specify a syntax, non-standard syntaxes will be
             : automatically inferred by the file extensions .scss, .sass,
             : .less, and .sss.

    * fix : bool, None
          : Automatically fix violations of certain rules.

    * custom_syntax : str, None
                    : Module name or path to a JS file exporting a
                    : PostCSS-compatible syntax.

    * ignore_disables : bool, None
                      : Ignore styleline-disable comments.

    * disable_default_ignores : bool, None
                              : Allow linting of node_modules and
                              : bower_components.

    * cache : bool, None
            : Store the info about processed files in order to only operate on
            : the changed ones the next time you run stylelint. By default, the
            : cache is stored in "./.stylelintcache". To adjust this, use
            : --cache-location.

    * cache_location : str, None
                     : Path to a file or directory to be used for the cache
                     : location.
                     : Default is "./.stylelintcache". If a directory is
                     : specified, a cache file will be created inside the
                     : specified folder, with a name derived from a hash of the
                     : current working directory.
                     :
                     : If the directory for the cache does not exist, make sure
                     : you add a trailing "/" on *nix systems or "\\" on
                     : Windows. Otherwise the path will be assumed to be a file.

    * formatter : str, None
                : The output formatter:
                : ${getFormatterOptionsText({ useOr: true })}.

    * custom_formatter : str, None
                       : Path to a JS file exporting a custom formatting
                       : function.

    * quiet : bool, None
            : Only register warnings for rules with an "error"-level severity
            : (ignore "warning"-level).

    * color    : bool, None
    * no_color : bool, None
               : Force enabling/disabling of color.

    * report_needless_disables : bool, None
                               : Report stylelint-disable comments that are not
                               : blocking a lint warning.
                               : The process will exit with code
                               : ${EXIT_CODE_ERROR} if needless disables are
                               : found.

    * max_warnings : int, None
                   : Number of warnings above which the process will exit with
                   : code ${EXIT_CODE_ERROR}.
                   : Useful when setting "defaultSeverity" to "warning" and
                   : expecting the process to fail on warnings (e.g. CI build).


Requirements:

    * node.js
    * stylelint
      to install, run `npm install --save-dev stylelint`

"""

import os
from pybuildtool import BaseTask, expand_resource

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def prepare(self):
        cfg = self.conf
        args = self.args

        # Specify a configuration file
        c = cfg.get('config_file')
        if c:
            args.append("--config='%s'" % expand_resource(self.group, c))

        self.add_bool_args('fix', 'ignore_disables', 'disable_default_ignores',
                'cache', 'quiet', 'color', 'no_color',
                'report_needless_disables')

        self.add_int_args('max_warning')

        self.add_str_args('config', 'config_basedir', 'ignore_path',
                'ignore_pattern', 'syntax', 'custom_syntax', 'cache_location',
                'formatter', 'custom_formatter')


    def perform(self):
        if self.file_out:
            self.bld.fatal('%s produces no output' % tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg} {in_}'.format(
            exe=executable,
            arg=' '.join(self.args),
            in_=' '.join(self.file_in),
        ))


def configure(conf):
    bin_path = 'node_modules/stylelint/bin/stylelint.js'
    conf.start_msg("Checking for program '%s'" % tool_name)
    if os.path.exists(bin_path):
        bin_path = os.path.realpath(bin_path)
        conf.end_msg(bin_path)
        conf.env['%s_BIN' % tool_name.upper()] = bin_path
    else:
        conf.end_msg('not found', color='YELLOW')
