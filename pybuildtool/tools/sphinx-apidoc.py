"""
Produce rst files for in code files documentation.

Options:

    * work_dir    : str, None
                    Change working directory
    * output_dir  : str, None, required
                    Output directory
    * project_dir : str, None, required
                    Location of python modules
    * exclude     : list, []
                    Skip the documentation in this files

Requirements:

    * sphinx
      to install, run `pip install sphinx`

"""
from pybuildtool import BaseTask, expand_resource, expand_wildcard, make_list

tool_name = __name__

class Task(BaseTask):

    name = tool_name
    workdir = None

    def prepare(self):
        cfg = self.conf
        args = self.args

        args.append('--force')

        c = cfg.get('work_dir')
        if c:
            self.workdir = expand_resource(self.group, c)
            if self.workdir is None:
                self.bld.fatal(cfg['work_dir'] + ' not found.')

        output_dir = expand_resource(self.group, cfg['output_dir'])
        if output_dir is None:
            self.bld.fatal(cfg['output_dir'] + ' not found.')
        args.append('-o ' + output_dir)

        project_dir = expand_resource(self.group, cfg['project_dir'])
        if project_dir is None:
            self.bld.fatal(cfg['project_dir'] + ' not found.')
        args.append(project_dir)

        for fname in make_list(cfg.get('exclude')):
            exclude_files = expand_wildcard(self.group, fname)
            if exclude_files is None:
                self.bld.fatal(fname + ' not found.')
            args.extend(exclude_files)


    def perform(self):
        if self.file_in:
            self.bld.fatal('%s takes no input' % tool_name.capitalize())
        if self.file_out:
            self.bld.fatal('%s produces no output' % tool_name.capitalize())

        kwargs = {}
        if self.workdir is not None:
            kwargs['cwd'] = self.workdir

        executable = self.env['SPHINX_APIDOC_BIN']
        return self.exec_command(
            '{exe} {arg} {in_}'.format(
                exe=executable,
                arg=' '.join(self.args),
                in_=' '.join(self.file_in),
            ),
            **kwargs)


def configure(conf):
    conf.env['SPHINX_APIDOC_BIN'] = conf.find_program('sphinx-apidoc')[0]
