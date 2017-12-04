r'''
Restores NuGet packages.

If a solution is specified, this command restores NuGet packages that are
installed in the solution and in projects contained in the solution. Otherwise,
the command restores packages listed in the specified packages.config file,
Microsoft Build project, or project.json file.

Options:
    * require_consent : bool, None
                      : Checks if package restore consent is granted before
                      : installing a package.

    * project_to_project_timeout : int, None
                                 : Timeout in seconds for resolving project to
                                 : project references.

    * packages_directory : str, None
                         : (OutputDirectory) Specifies the packages folder.

    * solution_directory : str, None
                         : Specifies the solution directory. Not valid when
                         : restoring packages for a solution.

    * msbuild_version : int, None
                      : Specifies the version of MSBuild to be used with this
                      : command.
                      : Supported values are 4, 12, 14.
                      : By default the MSBuild in your path is picked, otherwise
                      : it defaults to the highest installed version of MSBuild.

    * msbuild_path : str, None
                   : Specifies the path of MSBuild to be used with this command.
                   : This command will takes precedence over MSbuildVersion,
                   : nuget will always pick MSbuild from this specified path.

    * recursive : bool, None
                : Restore all referenced projects for UWP and NETCore projects.
                : This does not include packages.config projects.

    * source : list, None
             : A list of packages sources to use for this command.

    * fallback_source : list, None
                      : A list of package sources to use as fallbacks for this
                      : command.

    * no_cache : bool, None
               : Disable using the machine cache as the first package source.

    * direct_download : bool, None
                      : Download directly without populating any caches with
                      : metadata or binaries.

    * disable_parallel_processing : bool, None
                                  : Disable parallel processing of packages for
                                  : this command.

    * package_save_mode : str, None
                        : Specifies types of files to save after package
                        : installation: nuspec, nupkg, nuspec;nupkg.

    * verbosity : str, None
                : Display this amount of details in the output: normal, quiet,
                : detailed.

    * non_interactive : bool, None
                      : Do not prompt for user input or confirmations.

    * config_file : str, None
                  : The NuGet configuration file. If not specified,
                  : file %AppData%\NuGet\NuGet.config is used as configuration
                  : file.

    * force_english_output : bool, None
                           : Forces the application to run using an invariant,
                           : English-based culture.

Requirements:

    * nuget cli

'''
from pybuildtool import BaseTask, expand_resource, make_list

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def prepare(self):
        cfg = self.conf
        arg = self.args

        c = cfg.get('require_consent')
        if c:
            arg.append('-RequireConsent')

        c = cfg.get('project_to_project_timeout')
        if c:
            arg.append('-Project2ProjectTimeOut')
            arg.append('%i' % int(c))

        c = cfg.get('packages_directory')
        if c:
            arg.append('-PackagesDirectory')
            arg.append(c.format(**self.group.get_patterns()))

        c = cfg.get('solution_directory')
        if c:
            arg.append('-SolutionDirectory')
            arg.append(c.format(**self.group.get_patterns()))

        c = cfg.get('msbuild_version')
        if c:
            arg.append('-MSBuildVersion')
            arg.append('%i' % int(c))

        c = cfg.get('msbuild_path')
        if c:
            path = expand_resource(self.group, c)
            if path is None:
                self.bld.fatal('msbuild_path not found: ' + c)
            arg.append('-MSBuildPath')
            arg.append(path)

        c = cfg.get('recursive')
        if c:
            arg.append('-Recursive')

        sources = make_list(cfg.get('source'))
        for source in sources:
            path = expand_resource(self.group, source)
            if path is None:
                self.bld.fatal('source not found: ' + c)
            arg.append('-Source')
            arg.append(path)

        sources = make_list(cfg.get('fallback_source'))
        for source in sources:
            path = expand_resource(self.group, source)
            if path is None:
                self.bld.fatal('fallback_source not found: ' + c)
            arg.append('-FallbackSource')
            arg.append(path)

        c = cfg.get('no_cache')
        if c:
            arg.append('-NoCache')

        c = cfg.get('direct_download')
        if c:
            arg.append('-DirectDownload')

        c = cfg.get('disable_parallel_processing')
        if c:
            arg.append('-DisableParallelProcessing')

        c = cfg.get('package_save_mode')
        if c:
            arg.append('-PackageSaveMode')
            arg.append(c)

        c = cfg.get('verbosity')
        if c:
            arg.append('-Verbosity')
            arg.append(c)

        c = cfg.get('non_interactive')
        if c:
            arg.append('-NonInteractive')

        c = cfg.get('config_file')
        if c:
            path = expand_resource(self.group, c)
            if path is None:
                self.bld.fatal('config_file not found: ' + c)
            arg.append('-ConfigFile')
            arg.append(path)

        c = cfg.get('force_english_output')
        if c:
            arg.append('-ForceEnglishOutput')


    def perform(self):
        executable = self.env['%s_BIN' % tool_name.upper()]
        cmds = [executable, 'restore'] + self.args + self.file_in
        return self.exec_command(cmds)


def configure(conf):
    bin_path = conf.find_program('nuget.exe')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
