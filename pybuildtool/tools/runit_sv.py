"""
Manage runit services.

Options:

    * command  : str, None
               : service command to run, any of:
               : - start
               : - stop
               : - restart

    * target   : str, None
               : servcie directory to operate

    * wait_sec : int, None
               : wait for status changes before exit

    * force    : bool, False
               : forceful execution of service command

Requirements:

    * runit
      to install, for example run `apt-get install runit`
"""
from pybuildtool import BaseTask, expand_resource

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def prepare(self):
        cfg = self.conf
        args = self.args

        c = cfg.get('wait_sec', None)
        if c is not None:
            args.append('-w%s' % c)

        command = cfg.get('command', None)
        if command is None:
            self.bld.fatal('command option is required.')

        c = cfg.get('force', False)
        if c:
            args.append('force-' + command)
        else:
            args.append(command)

        target = cfg.get('target', None)
        if target:
            target = expand_resource(self.group, target)
        if target is None:
            self.bld.fatal('target option is required.')
        args.append(target)


    def perform(self):
        if self.file_in:
            self.bld.fatal('%s takes no input' % tool_name.capitalize())
        if self.file_out:
            self.bld.fatal('%s produces no output' % tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command([executable] + self.args)


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = conf.find_program('sv')[0]
