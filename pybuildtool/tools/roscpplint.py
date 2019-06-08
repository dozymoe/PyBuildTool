"""
CMake link commands for ROS packages. The lint commands perform static
checking of Python or C++ source code for errors and standards compliance.
See: http://wiki.ros.org/roslint

Options:

    * work_dir    : str, None, Change current directory
    * output      : str, None, By default, the output is formatted to ease
                    emacs parsing. Visual Studio compatible output (vs7) may
                    also be used. Other formats are unsupported.
                    Possible values: vs7
    * filter      : list, []
                    Specify category-filters to apply: only error messages
                    whose category names pass the filters will be printed.
                    Category names are printed with the message and look like
                    "[whitespace/indent]".
                    Filter are evaluated left to right.
                    "-FOO" and "FOO" means "do not print categories that start
                    with FOO"
                    "+FOO" means "do print categories that start with FOO".
    * counting    : str, None
                    The total number of errors found is always printed. If
                    'top level' is provided, then the count of errors in each
                    of the top-level categories like 'build' and 'whitespace'
                    will also be printed. If 'detailed' is provided, then a
                    count is provided for each category like 'build/class'.
                    Possible values: total, toplevel, detailed
    * root_dir    : str, None
                    The root directory used for deriving header guard CPP
                    variable. By default, the header guard CPP variable is
                    calculated as the relative path to the directory that
                    contains .git, .hg, or .svn. When this flag is specified,
                    the relative path is calculated from the specified
                    directory. If the specified directory does not exist, this
                    flag is ignored.
    * line_length : int, None
                    This is the allowed line length for the project. The
                    default value is 80 characters.
    * extensions  : list, ['c', 'cpp', 'h']
                    The allowed file extensions that cpplint will check.

Requirements:

    * roslint
      to install, ??

"""
import os
from pybuildtool import BaseTask, expand_resource, make_list

tool_name = __name__

class Task(BaseTask):

    name = tool_name
    workdir = None

    def prepare(self):
        cfg = self.conf
        args = self.args

        # Change current directory
        c = cfg.get('work_dir')
        if c:
            self.workdir = expand_resource(self.group, c)
            if self.workdir is None:
                self.bld.fatal(cfg['work_dir'] + ' not found.')

        # Output
        c = cfg.get('output')
        if c:
            args.append('--output=' + c)

        # Filters
        c = make_list(cfg.get('filter'))
        if c:
            args.append('--filter=' + ','.join(c))

        # Counting
        c = cfg.get('counting')
        if c:
            args.append('--counting=' + c)

        # Root
        c = cfg.get('root_dir')
        if c:
            args.append('--root=' + expand_resource(self.group, c))

        # Line length
        c = cfg.get('line_length')
        if c:
            args.append('--linelength=%i' % c)

        # Extensions
        c = make_list(cfg.get('extensions', ['c', 'cpp', 'h']))
        args.append('--extensions=' + ','.join(c))


    def perform(self):
        if self.file_out:
            self.bld.fatal("%s doesn't produce files" % tool_name.capitalize())

        kwargs = {}
        if self.workdir is not None:
            kwargs['cwd'] = self.workdir

        executable = self.env['%s_BIN' % tool_name.upper()]
        # TODO: roslint doesn't work in python3, xrange and bytes
        return self.exec_command(
            'python2 {exe} {arg} {in_}'.format(
                exe=executable,
                arg=' '.join(self.args),
                in_=' '.join(self.file_in),
            ),
            **kwargs)


def configure(conf):
    bin_path = '/usr/libexec/roslint/cpplint'
    conf.start_msg("Checking for program '%s'" % 'cpplint')
    if os.path.exists(bin_path):
        bin_path = os.path.realpath(bin_path)
        conf.end_msg(bin_path)
    else:
        conf.end_msg('not found', color='YELLOW')
        bin_path = conf.find_program('cpplint')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
