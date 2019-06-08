# pylint:disable=line-too-long
r'''
Run MSBuild.

Builds the specified targets in the project file. If a project file is not
specified, MSBuild searches the current working directory for a file that has
a file extension that ends in "proj" and uses that file.

Options:

    * target : list, None
             : Build these targets in this project.
             : Example:
             :   - Resources
             :   - Compile

    * property : list, None
               : Set or override these project-level properties. <n> is the
               : property name, and <v> is the property value.
               : Example:
               :   - WarningLevel=2
               :   - OutDir=bin\Debug\

    * max_cpu_count : int, None
                    : Specifies the maximum number of concurrent processes to
                    : build with. If the switch is not used, the default value
                    : used is 1. If the switch is used without a value MSBuild
                    : will use up to the number of processors on the computer.

    * tools_version : str, None
                    : The version of the MSBuild Toolset (tasks, targets, etc.)
                    : to use during build. This version will override the
                    : versions specified by individual projects.
                    : Example: 3.5

    * verbosity : str, None
                : Display this amount of information in the event log.
                : The available verbosity levels are:
                :   - q[uiet]
                :   - m[inimal]
                :   - n[ormal]
                :   - d[etailed]
                :   - diag[nostic]

    * console_logger_parameters : list, None
                                : Parameters to console logger.
                                : The available parameters are:
                                :   - PerformanceSummary
                                :     Show time spent in tasks, targets and
                                :     projects.
                                :   - Summary
                                :     Show error and warning summary at the end.
                                :   - NoSummary
                                :     Don't show error and warning summary at
                                :     the end.
                                :   - ErrorsOnly
                                :     Show only errors.
                                :   - WarningsOnly
                                :     Show only warnings.
                                :   - NoItemAndPropertyList
                                :     Don't show list of items and properties at
                                :     the start of each project build.
                                :   - ShowCommandLine
                                :     Show TaskCommandLineEvent messages
                                :   - ShowTimestamp
                                :     Display the Timestamp as a prefix to any
                                :     message.
                                :   - ShowEventId
                                :     Show eventId for started events, finished
                                :     events, and messages
                                :   - ForceNoAlign
                                :     Does not align the text to the size of
                                :     the console buffer
                                :   - DisableConsoleColor
                                :     Use the default console colors for all
                                :     logging messages.
                                :   - DisableMPLogging
                                :     Disable the multiprocessor logging style
                                :     of output when running in
                                :     non-multiprocessor mode.
                                :   - EnableMPLogging
                                :     Enable the multiprocessor logging style
                                :     even when running in non-multiprocessor
                                :     mode. This logging style is on by default.
                                :   - Verbosity
                                :     overrides the /verbosity setting for this
                                :     logger.
                                : Example:
                                :   - PerformanceSummary
                                :   - NoSummary
                                :   - Verbosity=minimal

    * no_console_logger : bool, None
                        : Disable the default console logger and do not log
                        : events to the console.

    * file_logger[n] : bool, None
                     : Logs the build output to a file. By default the file is
                     : in the current directory and named "msbuild[n].log".
                     : Events from all nodes are combined into a single log.
                     : The location of the file and other parameters for the
                     : fileLogger can be specified through the addition of the
                     : "/fileLoggerParameters[n]" switch.
                     : "n" if present can be a digit from 1-9, allowing up to
                     : 10 file loggers to be attached. (Short form: /fl[n])

    * file_logger_parameters[n] : list, None
                                : Provides any extra parameters for file
                                : loggers.
                                : The presence of this switch implies the
                                : corresponding /filelogger[n] switch.
                                : "n" if present can be a digit from 1-9.
                                : /fileloggerparameters is also used by any
                                : distributed file logger, see description of
                                : /distributedFileLogger.
                                :
                                : The same parameters listed for the console
                                : logger are available. Some additional
                                : available parameters are:
                                :   - LogFile
                                :     path to the log file into which the build
                                :     log will be written.
                                :   - Append
                                :     determines if the build log will be
                                :     appended to or overwrite the log file.
                                :     Setting the switch appends the build log
                                :     to the log file;
                                :     Not setting the switch overwrites the
                                :     contents of an existing log file.
                                :     The default is not to append to the log
                                :     file.
                                :   - Encoding
                                :     specifies the encoding for the file, for
                                :     example, UTF-8, Unicode, or ASCII
                                :
                                : Default verbosity is Detailed.
                                : Examples:
                                :   - LogFile=MyLog.log
                                :   - Append
                                :   - Verbosity=diagnostic
                                :   - Encoding=UTF-8

    * distributed_logger : list, None
                         : Use this logger to log events from MSBuild, attaching
                         : a different logger instance to each node. To specify
                         : multiple loggers, specify each logger separately.
                         : The <logger> syntax is:
                         : [<logger class>,]<logger assembly>[;<logger parameters>]  #  noqa
                         : The <logger class> syntax is:
                         : [<partial or full namespace>.]<logger class name>
                         : The <logger assembly> syntax is:
                         : {<assembly name>[,<strong name>] | <assembly file>}
                         : The <logger parameters> are optional, and are passed
                         : to the logger exactly as you typed them.
                         : Examples:
                         :   - XMLLogger,MyLogger,Version=1.0.2,Culture=neutral
                         :   - MyLogger,C:\My.dll*ForwardingLogger,C:\Logger.dll

    * distributed_file_logger : bool, None
                              : Logs the build output to multiple log files, one
                              : log file per MSBuild node. The initial location
                              : for these files is the current directory. By
                              : default the files are called
                              : "MSBuild<nodeid>.log". The location of the files
                              : and other parameters for the fileLogger can be
                              : specified with the addition of the
                              : "/fileLoggerParameters" switch.
                              :
                              : If a log file name is set through the
                              : fileLoggerParameters switch the distributed
                              : logger will use the fileName as a template and
                              : append the node id to this fileName to create a
                              : log file for each node.

    * logger : list, None
             : Use this logger to log events from MSBuild. To specify multiple
             : loggers, specify each logger separately.
             : The <logger> syntax is:
             : [<logger class>,]<logger assembly>[;<logger parameters>]
             : The <logger class> syntax is:
             : [<partial or full namespace>.]<logger class name>
             : The <logger assembly> syntax is:
             : {<assembly name>[,<strong name>] | <assembly file>}
             : The <logger parameters> are optional, and are passed to the
             : logger exactly as you typed them.
             : Examples:
             :   - XMLLogger,MyLogger,Version=1.0.2,Culture=neutral
             :   - XMLLogger,C:\Loggers\MyLogger.dll;OutputAsHTML

    * validate : str, None
               : Validate the project against the default schema or against the
               : specified schema.
               : Example: MyExtendedBuildSchema.xsd

    * ignore_project_extensions : list, None
                                : List of extensions to ignore when determining
                                : which project file to build.
                                : Example:
                                :   - .sln

    * node_reuse : bool, None
                 : Enables or Disables the reuse of MSBuild nodes.
                 : The parameters are:
                 :   - True
                 :     Nodes will remain after the build completes and will be
                 :     reused by subsequent builds (default)
                 :   - False
                 :     Nodes will not remain after the build completes

    * preprocess : str, None
                 : Creates a single, aggregated project file by inlining all the
                 : files that would be imported during a build, with their
                 : boundaries marked. This can be useful for figuring out what
                 : files are being imported and from where, and what they will
                 : contribute to the build. By default the output is written to
                 : the console window. If the path to an output file is provided
                 : that will be used instead.
                 : Example: out.txt

    * detailed_summary : bool, None
                       : Shows detailed information at the end of the build
                       : about the configurations built and how they were
                       : scheduled to nodes.

    * response_file : list, None
                    : Insert command-line settings from a text file.

    * no_auto_response : bool, None
                       : Do not auto-include any MSBuild.rsp files.

    * no_logo : bool, None
              : Do not display the startup banner and copyright message.

Requirements:

    * Microsoft Visual Studio

'''
# pylint:enable=line-too-long
import os
from pybuildtool import BaseTask, make_list, PATH

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def prepare(self):
        cfg = self.conf
        arg = self.args

        targets = make_list(cfg.get('target'))
        if targets:
            arg.append('/target:' + ';'.join(targets))

        properties = make_list(cfg.get('property'))
        if properties:
            arg.append('/property:' + ';'.join(properties))

        c = cfg.get('max_cpu_count')
        if c is not None:
            if not c:
                arg.append('/maxcpucount')
            else:
                arg.append('/maxcpucount:%i' % int(c))

        c = cfg.get('tools_version')
        if c:
            arg.append('/toolsversion:' + c)

        c = cfg.get('verbosity')
        if c:
            arg.append('/verbosity:' + c)

        params = make_list(cfg.get('console_logger_parameters'))
        if params:
            arg.append('/consoleloggerparameters:' + ';'.join(params))

        c = cfg.get('no_console_logger')
        if c:
            arg.append('/noconsolelogger')

        c = cfg.get('file_logger')
        if c:
            arg.append('/fileLogger')

        for n in range(1, 10):
            c = cfg.get('file_logger%i' % n)
            if c:
                arg.append('/fileLogger%i' % n)

        params = make_list(cfg.get('file_logger_parameters'))
        if params:
            arg.append('/fileloggerparameters:' + ';'.join(params))

        for n in range(1, 10):
            params = make_list(cfg.get('file_logger_parameters%i' % n))
            if params:
                arg.append('/fileloggerparameters%i:%s' % (n, ';'.join(params)))

        loggers = make_list(cfg.get('distributed_logger'))
        for logger in loggers:
            arg.append('/distributedlogger:' + logger)

        c = cfg.get('distributed_file_logger')
        if c:
            arg.append('/distributedFileLogger')

        loggers = make_list(cfg.get('logger'))
        for logger in loggers:
            arg.append('/logger:' + logger)

        c = cfg.get('validate')
        if c is not None:
            if c:
                arg.append('/validate:' + c)
            else:
                arg.append('/validate')

        c = make_list(cfg.get('ignore_project_extensions'))
        if c:
            arg.append('/ignoreprojectextensions:' + ';'.join(c))

        c = cfg.get('node_reuse')
        if c is not None:
            if c:
                arg.append('/nodeReuse:true')
            else:
                arg.append('/nodeReuse:false')

        c = cfg.get('preprocess')
        if c:
            arg.append('/preprocess:' + c)

        c = cfg.get('detailed_summary')
        if c:
            arg.append('/detailedsummary')

        files = make_list(cfg.get('response_file'))
        for file_ in files:
            arg.append('@' + file_)

        c = cfg.get('no_auto_response')
        if c:
            arg.append('/noautoresponse')

        c = cfg.get('no_logo')
        if c:
            arg.append('/nologo')


    def perform(self):
        executable = self.env['%s_BIN' % tool_name.upper()]
        cmds = [executable] + self.args + self.file_in
        return self.exec_command(cmds)


def configure(conf):
    bin_path = PATH(r'C:\Program Files (x86)\MSBuild\14.0\Bin\MSBuild.exe')
    conf.start_msg("Checking for program '%s'" % tool_name)
    if os.path.exists(bin_path):
        bin_path = os.path.realpath(bin_path)
        conf.end_msg(bin_path)
    else:
        conf.end_msg('not found', color='YELLOW')
        bin_path = conf.find_program('MSBuild.exe')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
