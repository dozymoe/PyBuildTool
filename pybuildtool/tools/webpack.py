"""
webpack is a module bundler for modern JavaScript applications.

Options:

    * mode : str, None
           : Enable production optimizations or development hints.
           : values: development, production, none
           : If not set it'd be inferred from environment variables.

    * config_file : str, None
                  : path to the config file
                  : default: webpack.config.js or webpackfile.js

    * env : list, None
          : environment passed to the config, when it is a function

    * context : str, None
              : the root directory for resolving entry point and stats
              : default: The current directory

    * entry : dict<str, str>, None
            : the entry point

    * debug : bool, None
            : switch loaders to debug mode

    * devtool : list, None
              : enable devtool for better debugging experience
              : example: --devtool eval-cheap-module-source-map

    * progress : bool, None
               : print compilation progress in percentage

    * module_bind : dict<str, str>, None
                  : bind an extension to a loader

    * module-bind-post : dict<str, str>, None
    * module-bind-pre  : dict<str, str>, None

    * output_path : str, None
                  : the output path for compilation assets
                  : default: The current directory

    * output_filename : str, None
                      : the output filename of the bundle
                      : default: [name].js

    * output_chunk_filename : str, None
                            : the output filename for additional chunks
                            : default: filename with [id] instead of [name] or
                              [id] prefixed

    * output_source_map_filename : str, None
                                 : the output filename for the SourceMap

    * output_public_path : str, None
                         : the public path for the assets

    * output_jsonp_function : str, None
                            : the name of the jsonp function used for chunk
                            : loading

    * output_pathinfo : bool, None
                      : include a comment with the request for every
                      : dependency (require, import, etc.)

    * output_library : str, None
                     : expose the exports of the entry point as library

    * output_library_target : str, None
                            : the type for exposing the exports of the entry
                            : point as library

    * records_input_path : str, None
                         : path to the records file (reading)

    * records_output_path : str, None
                          : path to the records file (writing)

    * records_path : str, None
                   : path to the records file

    * define : dict<str, str>, None
             : define any free var in the bundle

    * target : str, None
             : the targeted execution environment

    * cache : bool, None
            : enable in memory caching
            : default: It's enabled by default when watching

    * watch_stdin : bool, None
                  : exit the process when stdin is closed

    * watch_aggregate_timeout : int, None
                              : timeout for gathering changes while watching

    * watch_poll : bool, None
                 : the polling interval for watching (also enable polling)

    * hot : bool, None
          : enables Hot Module Replacement

    * prefetch : list, None
               : prefetch this request (Example: --prefetch ./file.js)

    * provide : dict<str, str>, None
              : provide these modules as free vars in all modules
              : example: --provide jQuery=jquery

    * labeled_modules : bool, None
                      : enables labeled modules

    * plugin : list, None
             : load this plugin

    * bail : bool, None
           : abort the compilation on first error

    * profile : bool, None
              : profile the compilation and include information in stats

    * resolve_alias : dict<str, str>, None
                    : setup a module alias for resolving
                    : example: jquery-plugin=jquery.plugin

    * resolve_extensions : list, None
                         : setup extensions that should be used to resolve
                         : modules
                         : example: --resolve-extensions .es6 .js

    * resolve_loader_alias : dict<str, str>, None
                           : setup a loader alias for resolving

    * optimize_max_chunks : int, None
                          : try to keep the chunk count below a limit

    * optimize_min_chunk_size : int, None
                              : try to keep the chunk size above a limit

    * optimize_minimize : bool, None
                        : minimize javascript and switches loaders to minimizing

    * color : bool, None
            : enables/Disables colors on the console
            : default: (supports-color)

    * sort_modules_by : str, None
                      : sorts the modules list by property in module

    * sort_chunks_by : str, None
                     : sorts the chunks list by property in chunk

    * sort_assets_by : str, None
                     : sorts the assets list by property in asset

    * hide_modules : bool, None
                   : hides info about modules

    * display_exclude : list, None
                      : exclude modules in the output

    * display_modules : bool, None
                      : display even excluded modules in the output

    * display_max_modules : int, None
                          : sets the maximum number of visible modules in output

    * display_chunks : bool, None
                     : display chunks in the output

    * display_entrypoints : bool, None
                          : display entry points in the output

    * display_origins : bool, None
                      : display origins of chunks in the output

    * display_cached : bool, None
                     : display also cached modules in the output

    * display_cached_assets : bool, None
                            : display also cached assets in the output

    * display_reasons : bool, None
                      : display reasons about module inclusion in the output

    * display_depth : bool, None
                    : display distance from entry point for each module

    * display_used_exports : bool, None
                           : display information about used exports in modules
                           : (Tree Shaking)

    * display_provided_exports : bool, None
                               : display information about exports provided from
                               : modules

    * display_error_details : bool, None
                            : display details about errors

    * verbose : bool, None
              : show more details


Requirements:

    * webpack, webpack-cli
      to install, `npm install webpack webpack-cli`

"""
import os
from pybuildtool import BaseTask, expand_resource

tool_name = __name__

class Task(BaseTask):

    name = tool_name
    workdir = None

    def prepare(self):
        cfg = self.conf
        args = self.args

        c = cfg.get('work_dir')
        if c:
            self.workdir = expand_resource(self.group, c)

        c = cfg.get('mode', os.environ.get('NODE_ENV'))
        if not c:
            if self.bld.variant in ('prod', 'production'):
                c = 'production'
            else:
                c = 'development'
        args.append('--mode=' + c)

        self.add_bool_args('debug', 'verbose', 'progress', 'output_pathinfo',
                'cache', 'watch_stdin', 'watch_poll', 'hot', 'labeled_modules',
                'bail', 'profile', 'optimize_minimize', 'color', 'hide_modules',
                'display_modules', 'display_chunks', 'display_entrypoints',
                'display_origins', 'display_cached', 'display_cached_assets',
                'display_reasons', 'display_depth', 'display_used_exports',
                'display_provided_exports', 'display_error_details')

        self.add_dict_args('module_bind', 'module_bind_pre', 'module_bind_post',
                'define', 'provide', 'resolve_alias', 'resolve_loader_alias',
                opt_val_sep=' ')

        self.add_int_args('watch_aggregate_timeout', 'optimize_max_chunks',
                'optimize_min_chunk_size', 'display_max_modules')

        self.add_list_args_multi('devtool', 'plugin', 'display_exclude')

        self.add_list_args_multi('env', opt_val_sep='.')
        self.add_list_args_multi('resolve_extensions', opt_val_sep=' ')

        self.add_path_args('context', 'records_input_path')

        self.add_path_list_args_multi('prefetch')

        self.add_str_args('output_path', 'output_filename',
                'output_chunk_filename', 'output_source_map_filename',
                'output_public_path', 'output_jsonp_function', 'output_library',
                'output_library_target', 'records_output_path', 'records_path',
                'target', 'sort_modules_by', 'sort_chunks_by', 'sort_assets_by',
                )

        c = cfg.get('config_file')
        if c:
            args.append('--config=' + expand_resource(self.group, c))

        c = cfg.get('entry', {})
        for entry_name, entry_js_file in c.items():
            args.append('--%s=%s' % (entry_name, expand_resource(
                    self.group, entry_js_file)))


    def perform(self):
        if len(self.file_out) > 1:
            self.bld.fatal('%s at most produces one output' %\
                    tool_name.capitalize())

        kwargs = {}
        if self.workdir is not None:
            kwargs['cwd'] = self.workdir

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            "{exe} {arg} {in_} {out}".format(
            exe=executable,
            arg=' '.join(self.args),
            in_=' '.join(self.file_in),
            out=' '.join(self.file_out),
        ),
        **kwargs)


def configure(conf):
    bin_path = 'node_modules/webpack-cli/bin/cli.js'
    conf.start_msg("Checking for program '%s'" % tool_name)
    if os.path.exists(bin_path):
        bin_path = os.path.realpath(bin_path)
        conf.end_msg(bin_path)
    else:
        conf.end_msg('not found', color='YELLOW')
        bin_path = conf.find_program('webpack')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
