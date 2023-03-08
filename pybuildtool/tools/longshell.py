"""
Run longshell commands.

Let's say you have a very long task like integration tests running in your waf
instance, you waited for a long time for it to finish. So you want to run
another waf instance parallel to that to quickly process the faster tasks but
you don't want to run another instance of the same integration tests because of
database conflicts.

This task is the same as the shell task but it will ensure you only run one
instance of the task. It is good for long running tasks that you don't want to
run more than one instance at a time.

The task will fail if it is already running.

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
#-
import locket
from pybuildtool import BaseTask, expand_resource
from pybuildtool.core.rule import token_to_filename

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

        lock_filename = '%s.longshell' % token_to_filename(
                self.group.get_name(), self.bld)
        try:
            with locket.lock_file(lock_filename, timeout=5):
                return self.exec_command(
                    '{exe} {arg} {in_}'.format(
                        exe=self.cmd,
                        arg=' '.join(self.args),
                        in_=' '.join(self.file_in),
                    ),
                    **kwargs)
        except locket.LockError:
            self.bld.to_log("Task %s has already started.\n" %\
                    self.group.get_name())
            return -1
