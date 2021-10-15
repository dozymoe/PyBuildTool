"""
Precompile handlebars templates.

Options:

    * amd          : bool, None, exports amd style (require.js)
    * commonjs     : bool, None, exports CommonJS style, path to Handlebars
                     module [default: null]
    * handlebarpath: str, None, path to handlebar.js (only valid for amd-style)
                     [default: ""]
    * known        : list, [], known helpers
    * knownOnly    : bool, None, known helpers only
    * minimize     : bool, None, minimize output
    * namespace    : str, None, template namespace
                     [default: 'Handlebars.templates']
    * simple       : bool, None, output template function only
    * root         : str, None, template root, base value that will be stripped
                     from template names
    * partial      : bool, None, compiling a partial template
    * data         : hash, None, include data when compiling
    * extension    : str, None, template extension [default: 'handlebars']
    * bom          : bool, None, removes the BOM (Byte Order Mark) from the
                     beginning of the templates

Requirements:

    * handlebars
      to install, edit package.json, run `npm install`
    * node.js

"""
import os
from json import dumps as json_dump
from pybuildtool import BaseTask, make_list

tool_name = __name__

class Task(BaseTask):

    conf = {
        '_replace_patterns_': ((r'\.handlebars$', '.js'),),
    }
    name = tool_name

    def prepare(self):
        cfg = self.conf
        args = self.args

        c = cfg.get('amd')
        if c:
            args.append('--amd')

        c = cfg.get('commonjs')
        if c:
            args.append('--commonjs')

        c = cfg.get('handlebarpath')
        if c:
            args.append("--handlebarPath='%s'" % c)

        for handler in make_list(cfg.get('known')):
            args.append("--known='%s'" % handler)

        c = cfg.get('known_only')
        if c:
            args.append('--knownOnly')

        c = cfg.get('minimize')
        if c:
            args.append('--min')

        c = cfg.get('namespace')
        if c:
            args.append("--namespace='%s'" % c)

        c = cfg.get('simple')
        if c:
            args.append('--simple')

        c = cfg.get('root')
        if c:
            args.append("--root='%s'" % c)

        c = cfg.get('partial')
        if c:
            args.append('--partial')

        c = cfg.get('data')
        if c:
            args.append("--data='%s'" % json_dump(c))

        c = cfg.get('extension')
        if c:
            args.append("--extension='%s'" % c)

        c = cfg.get('bom')
        if c:
            args.append('--bom')


    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal('%s only need one input' % tool_name.capitalize())
        if len(self.file_out) != 1:
            self.bld.fatal('%s can only have one output' %\
                    tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg} {in_} -f {out}'.format(
            exe=executable,
            arg=' '.join(self.args),
            in_=self.file_in[0],
            out=self.file_out[0],
        ))


def configure(conf):
    bin_path = 'node_modules/handlebars/bin/handlebars'
    conf.start_msg("Checking for program '%s'" % tool_name)
    if os.path.exists(bin_path):
        bin_path = os.path.realpath(bin_path)
        conf.end_msg(bin_path)
    else:
        conf.end_msg('not found', color='YELLOW')
        bin_path = conf.find_program('handlebars')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
