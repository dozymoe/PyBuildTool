"""
Preprocess CSS files using [Stylus](http://learnboost.github.io/stylus/).

Options:

    * work_dir : str, None
               : change current directory

    * use : list, None
          : utilize the Stylus plugin at <path>

    * inline : bool, None
             : use data URI

    * include : list, None
              : Add <path> to lookup paths

    * compress : bool, None
               : compress CSS output

    * firebug : bool, None
              : Emits debug infos in the generated CSS that can be used by the
              : FireStylus Firebug plugin

    * line_numbers : bool, None
                   : Emits comments in the generated CSS indicating the
                   : corresponding Stylus line

    * sourcemap : bool, None
                : Generates a sourcemap in sourcemaps v3 format

    * sourcemap_inline : bool, None
                       : Inlines sourcemap with full source text in base64
                       : format

    * sourcemap_root : str, None
                     : "sourceRoot" property of the generated sourcemap

    * sourcemap_base : str, None
                     : Base <path> from which sourcemap and all sources are
                     : relative

    * prefix : str, None
             : prefix all css classes

    * import : list, None
             : Import Stylus <file>

    * include_css : bool, None
                  : Include regular CSS on @import

    * deps : bool, None
           : Display dependencies of the compiled files

    * disable_cache : bool, None
                    : Disable caching

    * hoist_atrules : bool, None
                    : Move @import and @charset to the top

    * resolve_url : bool, None
                  : Resolve relative urls inside imports

    * resolve_url_nocheck : bool, None
                          : Like --resolve-url but without file existence check


Requirements:

    * node.js
    * stylus
      to install, run `npm install --save-dev stylus`

"""
import os
from pybuildtool import BaseTask, expand_resource

tool_name = __name__

class Task(BaseTask):

    name = tool_name
    conf = {
        '_replace_patterns_': ((r'\.styl$', '.css'),)
    }
    workdir = None

    def prepare(self):
        cfg = self.conf
        self.args = ['--print']

        c = cfg.get('work_dir')
        if c:
            self.workdir = expand_resource(self.group, c)

        self.add_bool_args('inline', 'compress', 'firebug', 'line_numbers',
                'sourcemap', 'sourcemap_inline', 'include_css', 'deps',
                'disable_cache', 'hoist_atrules', 'resolve_url',
                'resolve_url_nocheck')

        self.add_path_args('sourcemap_base', opt_val_sep=' ')

        self.add_path_list_args_multi('use', 'include', 'import',
                opt_val_sep=' ')

        self.add_str_args('sourcemap_root', 'prefix', opt_val_sep=' ')


    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal('%s only need one input, got %s' % (
                    tool_name.capitalize(), repr(self.file_in)))

        if len(self.file_out) != 1:
            self.bld.fatal('%s can only have one output, got %s ' % (\
                    tool_name.capitalize(), repr(self.file_out)))

        kwargs = {}
        if self.workdir is not None:
            kwargs['cwd'] = self.workdir

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg} < {in_} > {out}'.format(
            exe=executable,
            arg=' '.join(self.args),
            in_=self.file_in[0],
            out=self.file_out[0],
        ),
        **kwargs)


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
