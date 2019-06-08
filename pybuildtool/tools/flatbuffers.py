r"""
FlatBuffers is an efficient cross platform serialization library for C++, C#,
C, Go, Java, JavaScript, PHP, and Python. It was originally created at Google
for game development and other performance-critical applications.

Options:

    * binary : bool, None
             : Generate wire format binaries for any data definitions.

    * json : bool, None
           : Generate text output for any data definitions.

    * cpp : bool, None
          : Generate C++ headers for tables/structs.

    * go : bool, None
         : Generate Go files for tables/structs.

    * java : bool, None
           : Generate Java classes for tables/structs.

    * js : bool, None
         : Generate JavaScript code for tables/structs.

    * csharp : bool, None
             : Generate C# classes for tables/structs.

    * python : bool, None
             : Generate Python files for tables/structs.

    * php : bool, None
          : Generate PHP files for tables/structs.

    * output_dir : str, None, required
                 : Prefix PATH to all generated files.

    * include_dir : str, None
                  : Search for includes in the specified path.

    * strict_json : bool, None
                  : Strict JSON: field names must be / will be quoted,
                  : no trailing commas in tables/vectors.

    * allow_non_utf8 : bool, None
                     : Pass non-UTF-8 input through parser and emit nonstandard
                     : \x escapes in JSON. (Default is to raise parse error on
                     : non-UTF-8 input.)

    * defaults_json : bool, None
                    : Output fields whose value is the default when
                    :  writing JSON

    * unknown_json : bool, None
                   : Allow fields in JSON that are not defined in the
                   : schema. These fields will be discared when generating
                   : binaries.

    * no_prefix : bool, None
                : Don't prefix enum values with the enum type in C++.

    * scoped_enums : bool, None
                   : Use C++11 style scoped and strongly typed enums.
                   : also implies --no-prefix.

    * no_includes : bool, None
                  : Don't generate include statements for included
                  :  schemas the generated file depends on (C++).

    * gen_mutable : bool, None
                  : Generate accessors that can mutate buffers in-place.

    * gen_onefile : bool, None
                  : Generate single output file for C#.

    * gen_name_strings : bool, None
                       : Generate type name functions for C++.

    * escape_proto_ids : bool, None
                       : Disable appending '_' in namespaces names.

    * gen_object_api : bool, None
                     : Generate an additional object-based API.

    * cpp_ptr_type : str, None
                   : Set object API pointer type (default std::unique_ptr)

    * no_js_exports : bool, None
                    : Removes Node.js style export lines in JS.

    * goog_js_export : bool, None
                     : Uses goog.exports* for closure compiler exporting in JS.

    * raw_binary : bool, None
                 : Allow binaries without file_indentifier to be read.

This may crash flatc given a mismatched schema.

    * proto : bool, None
            : Input is a .proto, translate to .fbs.

    * grpc : bool, None
           : Generate GRPC interfaces for the specified languages

    * schema : bool, None
             : Serialize schemas instead of JSON (use with -b)

    * bfbs_comments : bool, None
                    : Add doc comments to the binary schema files.

    * conform : str, None
              : Specify a schema the following schemas should be
              : an evolution of. Gives errors if not.

    * conform_includes : str, None
                       : Include path for the schema given with --conform PATH

    * include_prefix : str, None
                     : Prefix this path to any generated include statements.

Requirements:

    * flatc
      to install, for example run `apt-get install flatbuffers`

"""
from pybuildtool import BaseTask, expand_resource

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def prepare(self):
        cfg = self.conf
        args = self.args

        self.add_bool_args('binary', 'json', 'cpp', 'go', 'java', 'js',
                'csharp', 'python', 'php', 'strict_json', 'allow_non_utf8',
                'defaults_json', 'unknown_json', 'no_prefix', 'scoped_enums',
                'no_includes', 'gen_mutable', 'gen_onefile', 'gen_name_strings',
                'escape_proto_ids', 'gen_object_api', 'no_js_exports',
                'goog_js_export', 'raw_binary', 'proto', 'grpc', 'schema',
                'bfbs_comments')

        self.add_path_args('conform', 'conform_includes', 'include_prefix')

        self.add_str_args('cpp_ptr_type')

        c = cfg.get('output_dir')
        if c is None:
            self.bld.fatal('Option output_dir is required.')
        else:
            output_dir = expand_resource(self.group, c)
            if output_dir is None:
                self.bld.fatal(c + ' was not found.')
            args.append('-o')
            args.append(output_dir)

        c = cfg.get('include_dir')
        if c:
            include_dir = expand_resource(self.group, c)
            if include_dir is None:
                self.bld.fatal(c + ' was not found.')
            args.append('-I')
            args.append(include_dir)


    def perform(self):
        if not self.file_in:
            self.bld.fatal('%s needs input' % tool_name.capitalize())
        if self.file_out:
            self.bld.fatal('%s produces no output' % tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg}'.format(
                exe=executable,
                arg=' '.join(self.args),
            ))


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = conf.find_program('flatc')[0]
