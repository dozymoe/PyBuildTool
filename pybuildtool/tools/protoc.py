""" Compiles .proto into .py using protobuf.

Protocol buffers are Google's language-neutral, platform-neutral, extensible
mechanism for serializing structured data – think XML, but smaller, faster, and
simpler. You define how you want your data to be structured once, then you can
use special generated source code to easily write and read your structured data
to and from a variety of data streams and using a variety of languages. 

Options:

    * proto_path : str, []
                 : Specify the directory in which to search for imports. May be
                 : specified multiple times; directories will be searched in
                 : order. If not given, the current working directory is used.
                 : If not found in any of these directories, the
                 : --descriptor_set_in descriptors will be checked for required
                 : proto file.

    * encode : str, None
             : Read a text-format message of the given type from standard input
             : and write it in binary to standard output. The message type must
             : be defined in PROTO_FILES or their imports.

    * decode : str, None
             : Read a binary message of the given type from standard input and
             : write it in the text format to standard output. The message type
             : must be defined in PROTO_FILES or their imports.

    * decode_raw : bool, None
                 : Read an arbitrary protocol message from standard input and
                 : write the raw tag/value pairs in text format to standard
                 : output. No PROTO_FILES should be given when using this flag.

    * descriptor_set_in : str, []
                        : Specifies a delimited list of FILES each containing
                        : a FileDescriptorSet (a protocol buffer defined in
                        : descriptor.proto).
                        : The FileDescriptor for each of the PROTO_FILES
                        : provided will be loaded from these FileDescriptorSets.
                        : If a FileDescriptor appears multiple times, the first
                        : occurence will be used.

    * descriptor_set_out : str, None
                         : Writes a FileDescriptorSet (a protocol buffer defined
                         : in descriptor.proto) containing all of the input
                         : files to FILE.

    * include_imports : bool, None
                      : When using --descriptor_set_out, also include all
                      : dependencies of the input files in the set, so that the
                      : set is self-contained.

    * include_source_info : bool, None
                          : When using --descriptor_set_out, do not strip
                          : SourceCodeInfo from the FileDescriptorProto.
                          : This results in vastly larger descriptors that
                          : include information about the original location of
                          : each decl in the source file as well as surrounding
                          : comments.

    * dependency_out : str, None
                     : Write a dependency output file in the format expected by
                     : make. This writes the transitive set of input file paths
                     : to FILE.

    * error_format : str, None
                   : Set the format in which to print errors.
                   : FORMAT may be 'gcc' (the default) or 'msvs' (Microsoft
                   : Visual Studio format).

    * print_free_field_numbers : bool, None
                               : Print the free field numbers of the messages
                               : defined in the given proto files. Group share
                               : the same field number space with the parent
                               : message. Extension ranges are counted as
                               : occupied fields numbers.

    * plugin : str, []
             : Specifies a plugin executable to use.
             : Normally, protoc searches the PATH for plugins, but you may
             : specify additional executables not in the path using this flag.
             : Additionally, EXECUTABLE may be of the form NAME=PATH, in which
             : case the given plugin name is mapped to the given executable even
             : if the executable's own name differs.

    * grpc_python_out : str, None
                      : Generate Python source file

    * python_out : str, None
                 : Generate Python source file

Requirements:

    * protobuf
      to install, run `pip install protobuf`

    * grpcio-tools
      to install, run `pip install grcpio-tools`
      you might need to specify the version

"""
from pybuildtool import BaseTask

tool_name = __name__

class Task(BaseTask):

    args_case = 'snake'
    name = tool_name

    def prepare(self):
        import pkg_resources

        cfg = self.conf

        self.args.append(__file__)

        self.add_path_list_args_multi('proto_path')

        self.add_str_args('encode', 'decode', 'error_format', 'plugin')

        self.add_bool_args('decode_raw', 'include_imports',
                'include_source_info', 'print_free_field_numbers')

        self.add_path_args('descriptor_set_in', 'descriptor_set_out',
                'dependency_out', 'grpc_python_out', 'python_out')

        proto_include = pkg_resources.resource_filename('grpc_tools', '_proto')
        self.args.append('-I{}'.format(proto_include))


    def perform(self):
        from grpc_tools import _protoc_compiler

        if self.file_out:
            self.bld.fatal('%s produces no output' % tool_name.capitalize())

        args = [arg.encode() for arg in self.args + self.file_in]
        print(args)
        return _protoc_compiler.run_main(args)


def configure(conf):
    conf.start_msg("Checking for program '%s'" % tool_name)
    try:
        import grpc_tools
        conf.end_msg('grpc_tools')
    except ImportError:
        conf.end_msg('not found', color='YELLOW')
