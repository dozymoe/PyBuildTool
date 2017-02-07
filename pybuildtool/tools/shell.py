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
    workdir = '.'
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

        self.cmd = cfg.get('commands').format(**self.group.get_patterns())


    def perform(self):
        cmd = '{exe} {arg} {in_}'
        return self.exec_command(
            cmd.format(
            exe=self.cmd,
            arg=' '.join(self.args),
            in_=' '.join(self.file_in),
            ),
            stdout=None,
            stderr=None,
            cwd=self.workdir,
        )
