"""
Validate python files.

Options:

    * work_dir         : str,      None,  change current directory before
                                          running pylint
    * error_only       : bool,     False,  only check for errors
    * config_file      : str,      None,  pylint configuration file
    * plugins          : list:str, [] ,   plugins to load (ex. pylint_django)
    * reporter         : str,      None,  custom reporter
    * full_report      : bool,     False, full report or only the messages
    * fail_cause       : list:str, [FATAL,ERROR,USAGE,CONVENTION], pylint exit
                         code unacceptable values
    * env              : dict:str, None,  shell environment variables

Requirements:

    * pylint
      to install, run `pip install pylint`

"""
from enum import Enum
import os
#-
from pybuildtool import BaseTask, expand_resource, make_list

tool_name = __name__


class PylintExitCode(Enum):
    """Exit codes for pylint

    See: https://pylint.pycqa.org/en/latest/user_guide/usage/run.html#exit-codes
    """
    FATAL = 1
    ERROR = 2
    WARNING = 4
    REFACTOR = 8
    CONVENTION = 16
    USAGE = 32


class Task(BaseTask):

    conf = {
        '_noop_retcodes_': [4],
    }
    name = tool_name
    workdir = None

    fail_clause = None
    envvars = None

    def prepare(self):
        cfg = self.conf
        args = self.args

        # Change current directory, before running pylint, helps module imports
        c = cfg.get('work_dir')
        if c:
            self.workdir = expand_resource(self.group, c)
            if self.workdir is None:
                self.bld.fatal(cfg['work_dir'] + ' not found.')

        # Specify a configuration file
        c = cfg.get('config_file')
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
        plugins = make_list(cfg.get('plugins'))
        if plugins:
            args.append('--load-plugins=%s' % ','.join(plugins))

        # Check pylint exit code
        c = cfg.get('fail_cause', ['FATAL', 'ERROR', 'USAGE', 'CONVENTION'])
        self.fail_clause = []
        for clause in c:
            self.fail_clause.append(getattr(PylintExitCode, clause).value)

        self.envvars = cfg.get('env')


    def perform(self):
        if not self.file_in:
            self.bld.fatal('%s for %s needs input' % (tool_name.capitalize(),
                    self.token_out[0]))

        if self.file_out:
            self.bld.fatal('%s produces no output' % tool_name.capitalize())

        kwargs = {}
        if self.workdir is not None:
            kwargs['cwd'] = self.workdir
        if self.envvars:
            env = os.environ.copy()
            env.update(self.envvars)
            kwargs['env'] = env

        executable = self.env['%s_BIN' % tool_name.upper()]
        ret = self.exec_command(
            '{exe} {arg} {in_}'.format(
                exe=executable,
                arg=' '.join(self.args),
                in_=' '.join(self.file_in),
            ),
            **kwargs)

        real_error = False
        for clause in self.fail_clause:
            real_error = real_error or (ret & clause)
        return real_error


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = conf.find_program(tool_name)[0]
