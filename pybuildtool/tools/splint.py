"""
Splint is a tool for statically checking C programs for security vulnerabilites
and coding mistakes. With minimal effort, Splint can be used as a better lint.
If additional effort is invested adding annotations to programs, Splint can
perform stronger checking than can be done by any standard lint.

Options:

    * work_dir : str, None, Change current directory
    * flags    : list, [], enable or disable checks

Requirements:

    * splint
      to install, for example run `apt-get install splint`

"""
from pybuildtool.core.task import Task as BaseTask
from pybuildtool.misc.path import expand_resource

tool_name = __name__

class Task(BaseTask):

    name = tool_name
    workdir = None

    def prepare(self):
        cfg = self.conf
        args = self.args

        # Change current directory, before running pylint, helps module imports
        c = cfg.get('work_dir')
        if c:
            self.workdir = expand_resource(self.group, c)

        # Flags
        c = cfg.get('flags', [])
        if len(c) == 0:
            # see: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=498809;msg=10
            c = [
                '-D__gnuc_va_list=va_list',
                '-warnposix',
                '+forcehints',
                '-formatcode',
                '-compdestroy',
            ]

        for flag in c:
            args.append(flag)


    def perform(self):
        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg} {in_}'.format(
            exe=executable,
            arg=' '.join(self.args),
            in_=' '.join(self.file_in),
        ), cwd=self.workdir)


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = conf.find_program(tool_name)[0]