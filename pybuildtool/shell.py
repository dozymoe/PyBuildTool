"""
Run shell commands.

Options:

    * work_dir     : str, None, change current directory before
                                running shell command
    * virtualenv   : str, None, python virtualenv directory
    * commands     : str, None, shell command
    * with_file_in : bool, True, set file-in files as argument to commands
"""

from base import Task as BaseTask, expand_resource

tool_name = __name__

class Task(BaseTask):

    conf = {
        '_source_grouped_': True,
    }
    name = tool_name
    prefix = []
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
            self.prefix.append('cd %s;' \
                % expand_resource(self.group, c))

        self.cmd = cfg.get('commands').format(**self.group.get_patterns())


    def perform(self):
        if self.conf.get('with_file_in', True):
            cmd = '{pre} {exe} {arg} {in_}'
        else:
            cmd = '{pre} {exe} {arg}'
        return self.exec_command(
            cmd.format(
            exe=self.cmd,
            pre=' '.join(self.prefix),
            arg=' '.join(self.args),
            in_=' '.join(self.file_in),
            ),
            stdout=None,
            stderr=None,
        )
