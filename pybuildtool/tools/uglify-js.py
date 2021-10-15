"""
UglifyJS is a JavaScript compressor/minifier written in JavaScript. It also
contains tools that allow one to automate working with Javascript code.

Options:

    * source_map : str, None
                 : Specify an output file where to generate source map

    * source_map_root : str, None
                      : The path to the original source to be included in the
                      : source map

    * source_map_url : str, None
                     : The path to the source map to be added in
                     : //# sourceMappingURL.
                     : Defaults to the value passed with --source-map

    * source_map_include_sources : bool, None
                                 : Pass this flag if you want to include the
                                 : content of source files in the source map as
                                 : sourcesContent property

    * in_source_map : str, None
                    : Input source map, useful if you're compressing JS
                    : that was generated from some other original code

    * screw_ie8 : bool, None
                : Pass this flag if you don't care about full compliance with
                : Internet Explorer 6-8 quirks (by default UglifyJS will try to
                : be IE-proof)

    * expr : bool, None
           : Parse a single expression, rather than a program (for parsing JSON)

    * prefix : str, None
             : Skip prefix for original filenames that appear in source maps.
             : For example --prefix 3 will drop 3 directories from file names
             : and ensure they are relative paths. You can also specify --prefix
             : relative, which will make UglifyJS figure out itself the relative
             : paths between original sources, the source map and the output
             : file

    * beautify : str, None
               : Beautify output/specify output options

    * mangle : list, None
             : Mangle names/pass mangler options

    * reserved : list, None
               : Reserved names to exclude from mangling

    * compress : str, None
               : Enable compressor/pass compressor options. Pass options like
               : --compress hoist_vars=false,if_return=false.
               : Use --compress with no argument to use the default compression
               : options

    * define : str, None
             : Global definitions

    * enclose : str, None
              : Embed everything in a big function, with a configurable
              : parameter/argument list

    * comments : str, None
               : Preserve copyright comments in the output.
               : By default this works like Google Closure, keeping JSDoc-style
               : comments that contain "@license" or "@preserve". You can
               : optionally pass one of the following arguments to this flag:
               :  - "all" to keep all comments
               :  - a valid JS regexp (needs to start with a slash) to keep
               :    only comments that match.
               : Note that currently not *all* comments can be kept when
               : compression is on, because of dead code removal or cascading
               : statements into sequences

    * preamble : str, None
               : Preamble to prepend to the output. You can use this to insert
               : a comment, for example for licensing information. This will
               : not be parsed, but the source map will adjust for its presence

    * stats : bool, None
            : Display operations run time on STDERR

    * acorn : bool, None
            : Use Acorn for parsing

    * spidermonkey : bool, None
                   : Assume input files are SpiderMonkey AST format (as JSON)

    * self : bool, None
           : Build itself (UglifyJS2) as a library (implies --wrap=UglifyJS
           : --export-all)

    * wrap : str, None
           : Embed everything in a big function, making the "exports" and
           : "global" variables available. You need to pass an argument to this
           : option to specify the name that your model will take when included
           : in, say, a browser

    * export_all : bool, None
                 : Only used when --wrap, this tells UglifyJS to add code to
                 : automatically export all globals

    * lint : bool, None
           : Display some scope warnings

    * verbose : bool, None
              : Verbose

    * noerr : bool, None
            : Don't throw an error for unknown options in --compress,
            : --beautify, --mangle


Requirements:

    * node.js
    * uglify-js
      to install, run `npm install --save-dev uglify-js`

"""
import os
from shutil import copyfile, Error
from pybuildtool import BaseTask

tool_name = __name__

class Task(BaseTask):

    name = tool_name
    conf = {
        '_replace_patterns_': ((r'\.js$', '.min.js'),),
    }

    def prepare(self):
        cfg = self.conf
        args = self.args

        self.add_bool_args('source_map_include_sources', 'screw_ie8', 'expr',
                'stats', 'acorn', 'spidermonkey', 'self', 'export_all', 'lint',
                'verbose', 'noerr')

        self.add_path_args('source_map_root', 'in_source_map')

        self.add_str_args('source_map', 'source_map_url', 'prefix', 'beautify',
                'reserved', 'define', 'enclose', 'preamble', 'wrap')

        if cfg.get('in_source_map', None):
            args.append("--in-source-map='%s'" % cfg['in_source_map'])

        for config in ('mangle', 'compress', 'comments'):
            if not config in cfg:
                continue

            c = cfg[config]
            if c:
                args.append("--%s='%s'" % (config, c))
            else:
                args.append('--' + config)


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
    bin_path = 'node_modules/uglify-js/bin/uglifyjs'
    conf.start_msg("Checking for program '%s'" % tool_name)
    if os.path.exists(bin_path):
        bin_path = os.path.realpath(bin_path)
        conf.end_msg(bin_path)
    else:
        conf.end_msg('not found', color='YELLOW')
        bin_path = conf.find_program('uglifyjs')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
