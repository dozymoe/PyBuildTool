"""
Wrapper around libsass.

Options:

    * work_dir : str, None
               : change current directory

    * omit_source_map_url : bool, None
                          : Omit source map URL comment from output

    * indented_syntax : bool, None
                      : Treat data from stdin as sass code (versus scss)

    * output_style : str, None
                   : CSS output style (nested | expanded | compact | compressed)

    * indent_type : str, None
                  : Indent type for output CSS (space | tab)

    * indent_width : int, None
                   : Indent width; number of spaces or tabs (maximum value: 10)

    * linefeed : str, None
               : Linefeed style (cr | crlf | lf | lfcr)

    * source_comments : bool, None
                      : Include debug info in output

    * source_map : str, None
                 : Emit source map (boolean, or path to output .map file)

    * source_map_contents : bool, None
                          : Embed include contents in map

    * source_map_embed : bool, None
                       : Embed sourceMappingUrl as data URI

    * source_map_root : bool, None
                      : Base path, will be emitted in source-map as is

    * include_path : str, None
                   : Path to look for imported files

    * follow : bool, None
             : Follow symlinked directories

    * precision : int, None
                : The amount of precision allowed in decimal numbers

    * importer : str, None
               : Path to .js file containing custom importer

    * functions : str, None
                : Path to .js file containing custom functions

Requirements:

    * node.js
    * node-sass
      to install, run `npm install --save-dev node-sass`

"""
import os
from pybuildtool import BaseTask, expand_resource

tool_name = __name__

class Task(BaseTask):

    name = tool_name
    conf = {
        '_replace_patterns_': ((r'\.scss$', '.css'),)
    }
    workdir = None

    def prepare(self):
        cfg = self.conf

        c = cfg.get('work_dir')
        if c:
            self.workdir = expand_resource(self.group, c)

        self.add_bool_args('omit_source_map_url', 'indented_syntax',
                'source_comments', 'source_map_contents', 'source_map_embed',
                'follow')

        self.add_int_args('indent_width', 'precision')

        self.add_path_args('source_map_root', 'importer', 'functions')

        self.add_path_list_args_multi('include_path')

        self.add_str_args('output_style', 'indent_type', 'linefeed',
                'source_map')


    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal("%s only need one input, got %s" % (
                    tool_name.capitalize(), repr(self.file_in)))

        if len(self.file_out) != 1:
            self.bld.fatal("%s can only have one output, got %s" % (
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
    bin_path = 'node_modules/node-sass/bin/node-sass'
    conf.start_msg("Checking for program '%s'" % tool_name)
    if os.path.exists(bin_path):
        bin_path = os.path.abspath(bin_path)
    else:
        bin_path = conf.find_program('node-sass')[0]
    conf.end_msg(bin_path)
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
