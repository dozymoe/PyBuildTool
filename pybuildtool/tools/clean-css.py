"""
Clean-css is a fast and efficient Node.js library for minifying CSS files.

Options:

    * keep-line-breaks     : bool, False, keep line breaks
    * no-comments          : bool, False, remove all special comments,
                             i.e /*! comment */
    * first-special-comment: bool, False, remove all special comments,
                             but the first one
    * root-path            : str, None, a root path to which resolve absolute
                             @import rules and rebase relative URLs
    * skip-import          : bool, False, disable @import processing
    * skip_rebase          : bool, False, disable URLs rebasing
    * skip-advanced        : bool, False, disable advanced optimizations -
                             selector & property merging, reduction, etc
    * skip-aggressive-merging: bool, False, disable properties merging based
                               on their order
    * rounding-precision   : int, 2, rounding precision
    * compatibility        : str, None, [ie7, ie8], force compatibility mode
    * timeout              : int, 5, per connection timeout when fetching
                             remote @imports (in seconds)
    * debug                : shows debug information (minification time &
                             compression efficiency)

Requirements:

    * clean-css
      to install, run `npm install --save-dev clean-css-cli`
    * node.js

"""
import os
from shutil import copyfile, Error
from pybuildtool import BaseTask

tool_name = __name__

class Task(BaseTask):

    conf = {
        '_replace_patterns_': ((r'\.css$', '.min.css'),),
    }
    name = tool_name

    def prepare(self):
        cfg = self.conf
        args = self.args

        # keep line breaks
        if cfg.get('keep-line-breaks', False):
            args.append('--keep-line-breaks')

        # remove all special comments, i.e /*! comment */
        if cfg.get('no-comments', False):
            args.append('--s0')

        # remove all special comments but the first one
        if cfg.get('first-special-comment', False):
            args.append('--s1')

        # a root path to which resolve absolute @import rules and rebase
        # relative URLs
        if cfg.get('root-path', None):
            args.append('--root=%s' % cfg['root-path'])

        # disable @import processing
        if cfg.get('skip-import', False):
            args.append('--skip-import')

        # disable URLs rebasing
        if cfg.get('skip_rebase', False):
            args.append('--skip-rebase')

        # disable advanced optimizations - selector & property merging,
        # reduction, etc
        if cfg.get('skip-advanced', False):
            args.append('--skip-advanced')

        # disable properties merging based on their order
        if cfg.get('skip-aggressive-merging', False):
            args.append('--skip-aggressive-merging')

        # rounding precision
        if cfg.get('rounding-precision', None):
            args.append('--rounding-precision=%s' % cfg['rounding-precision'])

        # force compatibility mode
        if cfg.get('compatibility', None):
            args.append('--compatibility=%s' % cfg['compatibility'])

        # per connection timeout when fetching remote @improts (in seconds)
        if cfg.get('timeout', None):
            args.append('--timeout=%s' % cfg['timeout'])

        # show debug information (minification time & compression efficiency)
        if cfg.get('debug', False):
            args.append('--debug')


    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal('%s only need one input' % tool_name.capitalize())
        if len(self.file_out) != 1:
            self.bld.fatal('%s only have one output' % tool_name.capitalize())

        if not self.is_production():
            try:
                copyfile(self.file_in[0], self.file_out[0])
                return 0
            except (IOError, Error):
                self.bld.fatal('cannot copy file to ' + self.file_out[0])
            return -1

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg} {in_} -o {out}'.format(
            exe=executable,
            arg=' '.join(self.args),
            in_=self.file_in[0],
            out=self.file_out[0],
        ))


def configure(conf):
    bin_path = 'node_modules/clean-css-cli/bin/cleancss'
    conf.start_msg("Checking for program '%s'" % tool_name)
    if os.path.exists(bin_path):
        bin_path = os.path.realpath(bin_path)
        conf.end_msg(bin_path)
    else:
        conf.end_msg('not found', color='YELLOW')
        bin_path = conf.find_program('cleancss')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
