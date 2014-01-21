PyBuildTool
===========

Summary
-------

PyBuildTool is build-tools platform written in python, with [Scons][1] as
its foundation.

There is demo project here [PyBuildToolExamples][2].

Basically you take some files, run a process that transform it into
different files or file types, using tools.

There are builtin tools, but you can make your own, see the modules in
**tools** directory as example, and read the documentation at [Scons][1],
simplest would be to create directory **site_scons/site_tools** at where the
**SConstruct** file is, then put your python modules there.

As a user, the only file you need to regularly maintain is **SConsfile.yml**.

If you specify **stage** parameter like so `scons --stage=development`, then
the name of your config file would be **SConsfile.development.yml**.

Example content of **SConsfile.yml**:

    tool_name:
        group_name:
            options:
                tool_parameter_1: "On"
                tool_parameter_2: "Off"
                _raw_:
                    - "--tool_parameter_3=On"
                    - "--without_tool_parameter_1"
            files:
                -
                    src: src/file1.in
                    dest: result/file1.out
                -
                    src:
                        - src/file2.in
                        - src/file3.in
                    dest: result/file4.out
        group_name_2:
            depends:
                - "tool_name:group_name"
            options:
                _target_sandboxed_: false
            files:
                -
                    src: result/file1.out
                    dest: completed/file5.out


`tool_name` will be the name of the tool, this is actually the name of
your tool python-module, the module will be loaded on demand using SCons
`env.Tool(tool_name)`.

`group_name` can be anything valid as YAML key, it is used to group files,
and tool configuration for those files. You can later target this group
during scons invocation, using `scons tool_name:group_name`.

You can specify the build dependencies of each target, per group, using
`depends`.
It is expected to be a list in the form of "tool_name:group_name", the same
format you would used to specifically build that target.

`options` will be passed to the tool's module as python dict. Some keys have
special meaning.

`_target_sandboxed_` is used by PyBuildTool.
The file results of each tool are by default sandboxed in a directory. Use
this option if you want to take it out into your own project directory.

`_raw_` will be interpreted by each tool, it should be read as is, and
supplied to the actual file processor as unmodified arguments.


Instruction
-----------

Clone this repository under the root directory of your project.

Copy **SConstruct.example** and **SConsfile.yml.example** to the root
directory of your project, or virtualenv, or where you are going to invoke
`scons` program from shell.

Modify **SConsfile.yml** per your project specifics.

If you keep **SConstruct** file as is, a **BUILD** directory will be created
as the sandbox.

Install "scons" using `pip install --egg SCons`, and other requirements that
each tool will needs, read their module file for more information.

**PyYAML** will also be needed to read the **SConsfile.yml**.



[1]: http://www.scons.org
[2]: http://github.com/dozymoe/PyBuildToolExamples
