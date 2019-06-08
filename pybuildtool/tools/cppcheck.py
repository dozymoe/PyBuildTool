"""
Generate documentation.

Options:

    * work_dir      : str, None, change current directory
    * build_dir     : str, None, Analysis output directory. Useful for various
                      data. Some possible usages are; whole program analysis,
                      incremental analysis, distributed analysis.
    * check_library : bool, None, Show information messages when library files
                      have incomplete info.
    * config_exclude: list, [], Path (prefix) to be excluded from
                      configuration checking. Preprocessor configurations
                      defined in headers (but not sources) matching the prefix
                      will not be considered for evaluation.

    * config_exclude_file: str, None, A file that contains a list of
                           config-excludes.

    * dump          : bool, None, Dump xml data for each translation unit. The
                      dump files have the extension .dump and contain ast,
                      tokenlist, symboldatabase, valueflow.
    * define        : list, [], Define preprocessor symbol.
    * undefine      : list, [], Undefine processor symbol. Explicitly hide
                      certain #ifdef code paths from checking.
    * enable_check  : list, [], Enable additional checks. The available ids are:
                      * all
                        Enable all checks. It is recommended to only use when
                        the whole program is scanned, because this enables
                        unusedFunction.
                      * warning
                        Enable warning messages.
                      * style
                        Enable all encoding style checks. All messages with the
                        severities 'style', 'performance' and 'portability' are
                        enabled.
                      * performance
                        Enable performance messages.
                      * portability
                        Enable portability messages.
                      * information
                        Enable information messages.
                      * unusedFunction
                        Check for unused functions. It is recommend to only
                        enable this when the whole program is scanned.
                      * missingInclude
                        Warn if there are missing includes. For detailed
                        information, use '--check-config'.
    * ignore_files  : list, [], Used when certain messages should be displayed
                      but should not cause a non-zero exitcode.
    * include_path  : list, [], Give path to search for include files. First
                      given path is search for contained header files first. If
                      paths are relative to source files, this is not needed.
    * include       : list, [], Force inclusion of a file before the checked
                      file. Can be used for example when checking the Linux
                      kernel, where autoconf.h needs to be included for every
                      file compiled. Works the same way as the GCC -include
                      option.
    * exclude       : list, [], Give a source file or source file directory to
                      exclude from the check. This applies only to source files
                      so header files include by source files are not matched.
                      Directory name is matched to all parts of the path.
    * inconclusive  : bool, None, Allow that Cppcheck reports even though the
                      analysis is inconclusive.
                      There are false positives with this option. Each result
                      must be carefully investigated before you know if it is
                      good or bad.
    * inline_disable: bool, True, Enable inline suppressions. Use them by
                      placing one or more comments, like:
                      `// cppcheck-suppress warningId` on the lines before the
                      warning to suppress.
    * jobs          : int, None, Start <jobs> threads to do the checking
                      simultaneously.
    * load_average  : float, None, Specifies that no new threads should be
                      started if there are other threads running and the load
                      average at least <load>.
    * proglang      : str, None, Forces cppcheck to check all files as the
                      given language. Valid values are: c, c++.
    * library       : str, None, Load file <cfg> that contains information
                      about types and functions. With such information
                      Cppcheck understands your code better and therefore you
                      get better results. The std.cfg file that is distributed
                      with Cppcheck is loaded automatically. For more
                      information about library files, read the manual.
    * project       : str, None, Run Cppcheck on project. The <file> can be a
                      Visual Studio Solution (*.sln), Visual Studio Project
                      (*.vcxproj), or compile databse (compile_commands.json).
                      The files to analyse, include paths, defines, platform
                      and undefines in the specified file will be used.
    * max_configs   : int, None, Maximum number of configurations to check in
                      a file before skipping it. Default is '12'. If used
                      together with '--force', the last option is the one that
                      is effective.
    * platform      : str, None, Specifies platform specific types and sizes.
                      The available builtin platforms are:
                      * unix32
                        32 bit unix variant
                      * unix64
                        64 bit unix variant
                      * win32A
                        32 bit Windows ASCII character encoding
                      * win32W
                        32 bit Windows UNICODE character encoding
                      * win64
                        64 bit Windows
                      * native
                        Unspecified platform. Type sizes of host system are
                        assumed, but no further assumptions.
    * quiet         : bool, True, Do not show progress reports.
    * relative_paths: list, [], Use relative paths in output. When given,
                      <paths> are used as base. You can separate multiple
                      paths by ';'. Otherwise path where source files are
                      searched is used. We use string comparison to create
                      relative paths, so using e.g. ~ for home folder does not
                      work. It is currently only possible to apply the base
                      paths to files that are on a lower level in the
                      directory tree.
    * rule          : str, None, Match regular expression.
    * rule_file     : str, None, Use given rule file. For more information,
                      see:
                      http://sourceforge.net/projects/cppcheck/files/Articles/
    * standard      : list, None, Set standard. The available options are:
                      * posix
                        POSIX compatible code
                      * c89
                        C code is C89 compatible
                      * c99
                        C code is C99 compatible
                      * c11
                        C code is C11 compatible (default)
                      * c++03
                        C++ code is C++03 compatible
                      * c++11
                        C++ code is C++11 compatible (default)
    * disable       : list, None, Suppress warnings that match <spec>, The
                      format of <spec> is:
                      [error id]:[filename]:[line]
                      The [filename] and [line] are optional. If [error id] is
                      a wildcard '*', all error ids match.
    * disable_file  : str, None, Suppress warnings listed in the file. Each
                      suppression is in the same format as <spec> above.
    * template      : str, None, Format the error messages. E.g.
                      '{file}:{line},{severity},{id},{message}' or
                      '{file}({line}):({severity}) {message}' or
                      '{callstack} {message}'
                      Pre-defined templates: gcc, vs, edit.
    * verbose       : bool, None, Output more detailed error information.
    * xml           : bool, None, Write results in xml format to error stream
                      (stderr).
    * xml_version   : str, None, Select the XML file version. Currently
                      versions 1 and 2 are available. The default version is
                      1.

Requirements:

    * cppcheck
      to install, for example run `apt-get install cppcheck`

"""
from pybuildtool import BaseTask, expand_resource, make_list

tool_name = __name__

class Task(BaseTask):

    name = tool_name
    workdir = None

    def prepare(self):
        cfg = self.conf
        args = self.args

        args.append('--error-exitcode=-1')

        # Change current directory, before running cppcheck
        c = cfg.get('work_dir')
        if c:
            self.workdir = expand_resource(self.group, c)
            if self.workdir is None:
                self.bld.fatal(cfg['work_dir'] + ' not found.')

        # Build dir
        c = cfg.get('build_dir')
        if c:
            args.append('--cppcheck-build-dir=' + expand_resource(self.group,
                    c))

        # Check library
        c = cfg.get('check_library')
        if c:
            args.append('--check-library')

        # Config exclude directory
        for path in make_list(cfg.get('config_exclude')):
            args.append('--config-exclude=' + expand_resource(self.group, path))

        # Config excludes file
        c = cfg.get('config_exclude_file')
        if c:
            args.append('--config-excludes-file=' + expand_resource(self.group,
                    c))

        # Dump
        c = cfg.get('dump')
        if c:
            args.append('--dump')

        # Defines
        for define in make_list(cfg.get('define')):
            args.append('-D' + define)

        # Undefines
        for define in make_list(cfg.get('undefine')):
            args.append('-U' + define)

        # Enable additional checks
        c = make_list(cfg.get('enable_check'))
        if c:
            args.append('--enable=' + ','.join(c))

        # Exit code suppressions
        for path in make_list(cfg.get('ignore_files')):
            args.append('--exitcode-suppressions=' + expand_resource(self.group,
                    path))

        # Search directory for include files
        for path in make_list(cfg.get('include_path')):
            args.append('-I ' + expand_resource(self.group, path))

        # Include
        for path in make_list(cfg.get('include')):
            args.append('--include=' + expand_resource(self.group, path))

        # Exclude
        for path in make_list(cfg.get('exclude')):
            args.append('-i ' + expand_resource(self.group, path))

        # Inconclusive, allow false positives
        c = cfg.get('inconclusive')
        if c:
            args.append('--inconclusive')

        # Inline suppression
        c = cfg.get('inline_disable', True)
        if c:
            args.append('--inline-suppr')

        # Parallel
        c = cfg.get('jobs')
        if c:
            args.append('-j %i' % c)

        # Max processor usage
        c = cfg.get('load_average')
        if c:
            args.append('-l %f' % c)

        # Programming language
        c = cfg.get('proglang')
        if c:
            args.append('--language=' + c)

        # Library
        c = cfg.get('library')
        if c:
            args.append('--library=' + expand_resource(self.group, c))

        # Project file
        c = cfg.get('project')
        if c:
            args.append('--project=' + expand_resource(self.group, c))

        # Maximum configs
        c = cfg.get('max_configs')
        if c:
            args.append('--max-configs=%i' % c)

        # Platform
        c = cfg.get('platform')
        if c:
            args.append('--platform=' + c)

        # Quiet
        c = cfg.get('quiet', True)
        if c:
            args.append('--quiet')

        # Relative paths
        c = make_list(cfg.get('relative_paths'))
        if c:
            args.append('--relative-paths=' + ';'.join(c))

        # Rule
        c = cfg.get('rule')
        if c:
            args.append("--rule='%s'" % c)

        # Rule file
        c = cfg.get('rule_file')
        if c:
            args.append('--rule-file=' + expand_resource(self.group, c))

        # Standard
        for std in make_list(cfg.get('standard')):
            args.append('--std=' + std)

        # Suppress
        for dis in make_list(cfg.get('disable')):
            args.append('--suppress=' + dis)

        # Suppressions list
        c = cfg.get('disable_file')
        if c:
            args.append('--suppressions-list=' + expand_resource(self.group,
                    c))

        # Template
        c = cfg.get('template')
        if c:
            args.append("--template='%s'" % c)

        # Verbose
        c = cfg.get('verbose')
        if c:
            args.append('--verbose')

        # XML
        c = cfg.get('xml')
        if c:
            args.append('--xml')

        # XML version
        c = cfg.get('xml_version')
        if c:
            args.append('--xml-version=' + c)


    def perform(self):
        if self.file_out:
            self.bld.fatal('%s produces no output' % tool_name.capitalize())

        kwargs = {}
        if self.workdir is not None:
            kwargs['cwd'] = self.workdir

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg} {in_}'.format(
                exe=executable,
                arg=' '.join(self.args),
                in_=' '.join(self.file_in),
            ),
            **kwargs)


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = conf.find_program(tool_name)[0]
