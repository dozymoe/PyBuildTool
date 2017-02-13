"""
Run shell commands.

Options:

    * work_dir     : str, None, change current directory before
                                running shell command
    * virtualenv   : str, None, python virtualenv directory
    * commands     : str, None, shell command

"""

from pybuildtool.core.task import Task as BaseTask
from pybuildtool.misc.path import expand_resource

tool_name = __name__

class Task(BaseTask):

    conf = {
        '_source_grouped_': True,
    }
    name = tool_name
    workdir = None
    cmd = None

    def prepare(self):
        cfg = self.conf

        # Virtualenv
        c = cfg.get('virtualenv', None)
        if c:
            self.prefix.append('source %s/bin/activate;' \
                % expand_resource(self.group, c))

        # Change current directory
        c = cfg.get('work_dir', None)
        if c:
            self.workdir = expand_resource(self.group, c)
            if self.workdir is None:
                self.bld.fatal(cfg['work_dir'] + ' not found.')

        self.cmd = cfg.get('commands').format(**self.group.get_patterns())


    def perform(self):
        if len(self.file_out) != 0:
            self.bld.fatal('%s produces no output' % tool_name.capitalize())

        kwargs = {'stdout': None, 'stderr': None}
        if self.workdir is not None:
            kwargs['cwd'] = self.workdir

        return self.exec_command(
            '{exe} {arg} {in_}'.format(
                exe=self.cmd,
                arg=' '.join(self.args),
                in_=' '.join(self.file_in),
            ),
            **kwargs)
