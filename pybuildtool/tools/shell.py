"""
Run shell commands.

Options:

    * work_dir : str, None
               : Change current directory before running shell command

    * command  : str, None
               : shell command

    * environ  : dict, None
               : Key value pair of shell environment.

    * fresh_environ : bool, False
                    : Starts with empty environment

"""
import os
from pybuildtool import BaseTask, expand_resource

tool_name = __name__

class Task(BaseTask):

    conf = {
        '_source_grouped_': True,
    }
    name = tool_name
    workdir = None
    cmd = None
    environ = None
    fresh_environ = None

    def prepare(self):
        cfg = self.conf

        # Change current directory
        c = cfg.get('work_dir', None)
        if c:
            self.workdir = expand_resource(self.group, c)
            if self.workdir is None:
                self.bld.fatal(c + ' not found.')
        else:
            c = os.environ.get('ROOT_DIR')
            if c:
                self.workdir = c

        c = cfg.get('command')
        if c:
            self.cmd = c.format(**self.group.get_patterns())
        else:
            self.bld.fatal('command option is required.')

        # Shell environment
        self.environ = {}
        c = cfg.get('environ', None)
        if c:
            for key, value in c.items():
                self.environ[key] = value.format(**self.group.get_patterns())

        self.fresh_environ = cfg.get('fresh_environ', False)


    def perform(self):
        if self.file_out:
            self.bld.fatal('%s produces no output' % tool_name.capitalize())

        if self.fresh_environ:
            environ = {k: v for k, v in os.environ.items() if k in ('PATH',)}
        else:
            environ = os.environ.copy()
        for key, value in self.environ.items():
            environ[key] = value

        kwargs = {
            'stdout': None,
            'stderr': None,
            'shell': True,
            'env': environ,
        }
        if self.workdir is not None:
            kwargs['cwd'] = self.workdir

        return self.exec_command(
            '{exe} {arg} {in_}'.format(
                exe=self.cmd,
                arg=' '.join(self.args),
                in_=' '.join(self.file_in),
            ),
            **kwargs)
