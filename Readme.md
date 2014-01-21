PyBuildTool
===========

* License      : MIT
* Project URL  : [PyBuildTool][3]
* Project Wiki : [Wiki at PyBuildTool][4]

Summary
-------

PyBuildTool is build-tools platform written in python, with [Scons][1] as
its foundation.

There is demo project here [PyBuildToolExamples][2].

Basically you take some files, run a process that transform them into
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

`options` will be passed to the tool's module as python dict. Some keys have
special meaning.

`_source_sandboxed_` is used by `scons --watch`.
Or used by any other tools that need to differentiate between transition files
and real source files which the user modified.

`_target_sandboxed_` is used by PyBuildTool.
The file results of each tool are by default sandboxed in a directory. Use
this option if you want to take it out into your own project directory.

`_raw_` will be interpreted by each tool, it should be read as is, and
supplied to the actual file processor as unmodified arguments.


Install
-------

Clone this repository under the root directory of your project.

Copy **SConstruct.example** and **SConsfile.yml.example** to the root
directory of your project, or virtualenv, or where you are going to invoke
`scons` program from shell.

Modify **SConsfile.yml** per your project specifics.

If you keep **SConstruct** file as is, a **BUILD** directory will be created
as the sandbox.

Install "scons" using `pip install --egg SCons`, and other requirements that
each tool will need, read their module file for more information.

**PyYAML** will also be needed to read the **SConsfile.yml**.



[1]: http://www.scons.org
[2]: http://github.com/dozymoe/PyBuildToolExamples
[3]: http://github.com/dozymoe/PyBuildTool
[4]: http://github.com/dozymoe/PyBuildTool/wiki
