"""
Validate python files.

Requirements:

    * pylint (python library)

Options:

    * work_dir         : str,      None,  change current directory before
                                          running pylint
    * error_only       : bool,     False,  only check for errors
    * config_file      : str,      None,  pylint configuration file
    * plugins          : list:str, [] ,   plugins to load (ex. pylint_django)
    * reporter         : str,      None,  custom reporter
    * full_report      : bool,     False, full report or only the messages
"""

from base import Task as BaseTask, expand_resource

tool_name = __name__

class Task(BaseTask):
    workdir = '.'

    def prepare_args(self):
        cfg = self.conf
        args = []

        # Change current directory, before running pylint, helps module imports
        c = cfg.get('work_dir', None)
        if c:
            self.workdir = expand_resource(self.group, c)

        # Specify a configuration file
        c = cfg.get('config_file', None)
        if c:
            args.append("--rcfile='%s'" % expand_resource(self.group, c))

        # Set the output format. Available formats are text,
        # parseable, colorized, msvs (visual studio) and html.
        # You can also give a reporter class, eg
        # mypackage.mymodule.MyReporterClass. [current: text]
        c = cfg.get('reporter', None)
        if c:
            args.append("--output-format='%s'" % c)

        # In error mode, checkers without error messages are
        # disabled and for others, only the ERROR messages are
        # displayed, and no reports are done by default
        c = cfg.get('error_only', False)
        if c:
            args.append('--errors-only')

        # Tells whether to display a full report or only the
        # messages [current: yes]
        c = cfg.get('full_report', False)
        if c:
            args.append('--reports=y')
        else:
            args.append('--reports=n')

        # Plugins
        plugins = cfg.get('plugins', [])
        if not isinstance(plugins, list):
            plugins = [plugins]
        if plugins:
            args.append('--load-plugins=%s' % ','.join(plugins))

        return args


    def perform(self):
        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            'cd {cwd}; {exe} {arg} {in_}'.format(
            exe=executable,
            arg=' '.join(self.prepare_args()),
            in_=' '.join(self.file_in),
            cwd=self.workdir,
        ))


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = conf.find_program(tool_name)[0]
