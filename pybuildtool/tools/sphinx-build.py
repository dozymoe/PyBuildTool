"""
Sphinx is a tool that makes it easy to create intelligent and beautiful
documentation, written by Georg Brandl and licensed under the BSD license.

It was originally created for the Python documentation, and it has excellent
facilities for the documentation of sofware projects in a range of languages.

Options:

    * builder    : str, html
                   Builder to use; default is html.
    * source_dir : str, None, required
                   Source directory.
    * output_dir : str, None, required
                   Output directory.
    * temp_dir   : str, None
                   Path for the cached environment and doctree files
                   (default: output_dir/.doctrees)
    * conf_dir   : str, None
                   Path where configuration file (conf.py) is located
                   (default: same as sourcedir).
    * settings   : dict, {}
                   Override setting in configuration file.
    * context    : dict, {}
                   Pass a value into HTML templates.
    * jobs       : int, None
                   Build in parallel with N processes where possible.

Requirements:

    * sphinx
      to install, run `pip install sphinx`

"""
from pybuildtool import BaseTask, expand_resource

tool_name = __name__

class Task(BaseTask):

    name = tool_name
    workdir = None

    def prepare(self):
        cfg = self.conf
        args = self.args

        c = cfg.get('work_dir')
        if c:
            self.workdir = expand_resource(self.group, c)
            if self.workdir is None:
                self.bld.fatal(cfg['work_dir'] + ' not found.')

        source_dir = expand_resource(self.group, cfg['source_dir'])
        if source_dir is None:
            self.bld.fatal(cfg['source_dir'] + ' not found.')
        args.append(source_dir)

        output_dir = expand_resource(self.group, cfg['output_dir'])
        if output_dir is None:
            self.bld.fatal(cfg['output_dir'] + ' not found.')
        args.append(output_dir)

        c = cfg.get('temp_dir')
        if c:
            temp_dir = expand_resource(self.group, c)
            if temp_dir is None:
                self.bld.fatal(c + ' not found.')
            args.append('-d ' + temp_dir)

        c = cfg.get('conf_dir')
        if c:
            conf_dir = expand_resource(self.group, c)
            if conf_dir is None:
                self.bld.fatal(c + ' not found.')
            args.append('-c ' + conf_dir)

        c = cfg.get('builder', 'html')
        args.append('-b ' + c)

        c = cfg.get('jobs')
        if c:
            args.append('-j %i' % c)

        c = cfg.get('settings', {})
        for key, value in c.items():
            args.append('-D %s=%s' % (key, value))

        c = cfg.get('context', {})
        for key, value in c.items():
            args.append('-A %s=%s' % (key, value))


    def perform(self):
        if self.file_out:
            self.bld.fatal('%s produces no output' % tool_name.capitalize())

        kwargs = {}
        if self.workdir is not None:
            kwargs['cwd'] = self.workdir

        executable = self.env['SPHINX_BUILD_BIN']
        return self.exec_command(
            '{exe} {arg} {in_}'.format(
                exe=executable,
                arg=' '.join(self.args),
                in_=' '.join(self.file_in),
            ),
            **kwargs)


def configure(conf):
    conf.env['SPHINX_BUILD_BIN'] = conf.find_program('sphinx-build')[0]
