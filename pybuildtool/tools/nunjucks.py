"""
A rich and powerful templating language for JavaScript.

Options:

    * force   : bool, False, force compilation to continue on error
    * filters : list, [], give the compiler a comma-delimited list of
                asynchronous filters, required for correctly generating code
    * name    : str, None, specify the template name when compiling a single
                file
    * basedir : str, None, if `basedir` is set, `name` will be ignored
                used to automatically generate `name`
    * include : list, None, include a file or folder which match the regex but
                would otherwise be excluded
                you can use this flag multiple times
                default: ["\\.html$", "\\.jinja$"]
    * exclude : list, None, exclude a file or folder which match the regex but
                would otherwise be included
                you can use this flag multiple times
                default: []

Requirements:

    * node.js
    * nunjucks
      to install, run `npm install --save-dev nunjucks`

"""
import os
from pybuildtool import BaseTask, expand_resource, make_list

tool_name = __name__

class Task(BaseTask):

    conf = {
        '_replace_patterns_': ((r'\.html', '.js'),),
    }
    name = tool_name

    def prepare(self):
        cfg = self.conf
        args = self.args

        # Change current directory
        c = cfg.get('force', False)
        if c:
            args.append('--force')

        c = make_list(cfg.get('filters'))
        if c:
            args.append('--filters="%s"' % ','.join(c))

        c_basedir = cfg.get('basedir', None)
        c = cfg.get('name', None)
        if c and c_basedir is not None:
            args.append('--name="%s"' % c)

        c = make_list(cfg.get('include'))
        for o in c:
            args.append('--include="%s"' % expand_resource(self.group, o))

        c = make_list(cfg.get('exclude'))
        for o in c:
            args.append('--exclude="%s"' % expand_resource(self.group, o))


    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal('%s only need one input' % tool_name.capitalize())
        if len(self.file_out) != 1:
            self.bld.fatal('%s can only have one output' %\
                    tool_name.capitalize())

        file_in = self.file_in[0]
        basedir = self.conf.get('basedir', None)
        if basedir:
            basedir = expand_resource(self.group, basedir)
            if file_in.startswith(basedir):
                name = file_in[len(basedir) + 1:]
            else:
                name = os.path.basename(file_in)
            self.args.append('--name="%s"' % name)

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg} {in_} > {out}'.format(
            exe=executable,
            arg=' '.join(self.args),
            in_=self.file_in[0],
            out=self.file_out[0]
        ))


def configure(conf):
    bin_path = 'node_modules/nunjucks/bin/precompile'
    conf.start_msg("Checking for program '%s'" % tool_name)
    if os.path.exists(bin_path):
        bin_path = os.path.realpath(bin_path)
        conf.end_msg(bin_path)
        conf.env['%s_BIN' % tool_name.upper()] = bin_path
    else:
        conf.end_msg('not found', color='YELLOW')
