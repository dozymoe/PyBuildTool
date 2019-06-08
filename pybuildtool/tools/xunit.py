""" xUnit.net console test runner

Input files could be list of pairs of assembly file and config file.
Configuration files must end in .config

Options:

    * parallel : str, None
               : Set parallelization based on option
               : Available values:
               :   none : turn off all parallelization
               :   collections : only parallelize collections
               :   assemblies : only parallelize assemblies
               :   all : parallelize assemblies & collection

    * max_threads : int, None
                  : Maximum thread count for collection parallelization
                  :   0 : run with unbounded thread count
                  :   >0 : limit task thread pool size to 'count'

    * no_shadow : bool, None
                : Do not shadow copy assemblies

    * team_city : bool, None
                : Forces TeamCity mode (normally auto-detected)

    * appveyor : bool, None
               : Forces AppVeyor CI mode (normally auto-detected)

    * no_logo : bool, None
              : Do not show the copyright message

    * quiet : bool, None
            : Do not show progress messages

    * serialize : bool, None
                : Serialize all test cases (for diagnostic purposes only

    * traits : dict, None
             : Only run tests with matching name/value traits
             : If specified more than once, acts as an OR operation

    * no_traits : dict, None
                : Do not run tests with matching name/value traits
                : If specified more than once, acts as an AND operation

    * methods : list, None
              : Run a given test method (should be fully specified;
              : i.e., 'MyNamespace.MyClass.MyTestMethod')
              : If specified more than once, acts as an OR operation

    * classes : list, None
              : Run all methods in a given test class (should be fully
              : specified; i.e., 'MyNamespace.MyClass')
              : If specified more than once, acts as an OR operation

    * reports : dict, None
              : Pairs of output style and filename.
              : Available output styles:
              :   xml : output results to xUnit.net v2 style XML file
              :   xmlv1 : output results to xUnit.net v1 style XML file
              :   nunit : output results to NUnit-style XML file
              :   html : output results to HTML file

Requirements:

    * xunit
      to install, for example run `choco install xunit`

"""
import os
from pybuildtool import BaseTask, expand_wildcard, make_list

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def prepare(self):
        cfg = self.conf
        args = self.args

        # Set parallelization
        c = cfg.get('parallel')
        if c is not None:
            args.append('-parallel')
            args.append(c)

        # Maximum thread count
        c = cfg.get('max_threads')
        if c is not None:
            args.append('-maxthreads')
            args.append(c)

        # Shadow copy
        c = cfg.get('no_shadow')
        if c:
            args.append('-noshadow')

        # TeamCity mode
        c = cfg.get('teamcity')
        if c:
            args.append('-teamcity')

        # AppVeyor CI mode
        c = cfg.get('appveyor')
        if c:
            args.append('-appveyor')

        # No logo
        c = cfg.get('no_logo')
        if c:
            args.append('-nologo')

        # Quiet
        c = cfg.get('quiet')
        if c:
            args.append('-quiet')

        # Serialize
        c = cfg.get('serialize')
        if c:
            args.append('-serialize')

        # Trait
        c = cfg.get('traits', {})
        for key, value in c.items():
            args.append('-trait')
            args.append('%s=%s' % (key, value))

        # No trait
        c = cfg.get('no_traits', {})
        for key, value in c.items():
            args.append('-notrait')
            args.append('%s=%s' % (key, value))

        # Methods
        for method in make_list(cfg.get('methods')):
            args.append('-method')
            args.append(method)

        # Classes
        for cls in make_list(cfg.get('classes')):
            args.append('-class')
            args.append(cls)

        # Reports
        c = cfg.get('reports', {})
        for key, value in c.items():
            if key not in ('xml', 'xmlvi', 'nunit', 'html'):
                self.bld.fatal('Unknown xunit report style: %s.' % key)

            args.append('-' + key)
            args.append(os.path.realpath(expand_wildcard(self.group, value)))


    def perform(self):
        if self.file_out:
            self.bld.fatal('%s produces no output' % tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg} {in_}'.format(
                exe=executable,
                arg=' '.join(self.args),
                in_=' '.join(self.file_in),
            ))


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] =\
            conf.find_program('xunit.console')[0]
