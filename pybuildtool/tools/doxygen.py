"""
Generate documentation.

Options:

    * work_dir      : str, None, change current directory
    * config_file   : str, None, doxygen configuration file

Requirements:

    * doxygen
      to install, for example run `apt-get install doxygen`

"""
from pybuildtool import BaseTask, expand_resource

tool_name = __name__

class Task(BaseTask):

    name = tool_name
    workdir = None

    def prepare(self):
        cfg = self.conf
        args = self.args

        # Change current directory, before running pylint, helps module imports
        c = cfg.get('work_dir', None)
        if c:
            self.workdir = expand_resource(self.group, c)
            if self.workdir is None:
                self.bld.fatal(cfg['work_dir'] + ' not found.')

        # Specify a configuration file
        c = cfg.get('config_file', None)
        if c:
            args.append(expand_resource(self.group, c))


    def perform(self):
        if self.file_in:
            self.bld.fatal('%s takes no input' % tool_name.capitalize())
        if self.file_out:
            self.bld.fatal('%s produces no output' % tool_name.capitalize())

        kwargs = {}
        if self.workdir is not None:
            kwargs['cwd'] = self.workdir

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg}'.format(
                exe=executable,
                arg=' '.join(self.args),
            ),
            **kwargs)


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = conf.find_program(tool_name)[0]
