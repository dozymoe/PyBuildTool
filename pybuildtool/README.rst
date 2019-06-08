PyBuildTool
===========

* License      : MIT
* Project URL  : http://github.com/dozymoe/PyBuildTool


Summary
-------

PyBuildTool helps transform resources and run automated tests as you code, I
usually have it watched the project files while editing with vim.

PyBuildTool is written in python as a higher level interface to `Waf
<http://waf.io>`_, a meta build system.

The configuration file you'd interact with: ``build.yml``, is declarative,
written in yaml. While the build tools which you could also write, were made to
be simple, following a pattern.

The configuration file does not need to be named "build.yml", just change
the file ``wscript`` (this is something that waf needs). You need to create
``wscript`` file yourself, following the example here:
http://raw.githubusercontent.com/dozymoe/PyBuildTool/master/pybuildtool/wscript.example

There are builtin tools, you can use them as examples to build your own build
tools, see them here: http://github.com/dozymoe/PyBuildTool/tree/master/pybuildtool/tools.
See how they were imported by the ``wscript`` file.

Since you control the ``wscript`` file, you control much of the aspect of the
build process.

If you wanted to go deeper than just editing ``build.yml`` you could read
`introduction to waf and wscript <http://waf.io/apidocs/tutorial.html>`_, or
a more technical `waf project structure <http://waf.io/book/#_basic_project_structure>`_.

There're three stages predefined: "dev", "stage", and "prod" (see the
``wscript`` file), but the functionality isn't there yet, they have separate
temporary build directory of their own but they still share the same build
rules.

Currently stages were implemented like this: for ``clean-css`` tool, if the
current stage was one of "dev" or "devel" or "development" it will do copy
operation instead of css file minification.

This is an example of ``build.yml``, pretend it's a django project:

.. code:: yaml

    # Macro, reusable definition, defined once - used plenty.
    # The word started with ampersand (&) is called yaml node anchor.
    # The anchor is what matters, it's a yaml feature.
    #
    # Group name in all uppercase will be ignored.
    #
    # {_1} is a replacement pattern for parent group's name at level 1.
    # It is being used to easily reproduce the directory structure.
    JSHINT_EXCLUDES: &JSHINT_EXCLUDES
        - "{_1}/{_2}/js/jquery.js"
        - "{_1}/{_2}/js/require.js"
        - "{_1}/{_2}/js/underscore.js"


    # Build group at level 1.
    djangoprj:
        # This is special, not a group.
        options:
            # Lower level tool configurations can be defined at higher level.
            #
            # `config_file` of the tool `jshint`
            jshint_config_file: "etc/jshint.rc"
            # `config_file` of the tool `pylint`
            pylint_config_file: "etc/pylint.rc"

        # Build group at level 2
        blogapp:
            # The lowest level group is the tool being used, if no such tool
            # was found a fatal error will be raised.
            jshint:
                # Wildcards is a okay, see ant-glob.
                file_in: "{_1}/{_2}/js/**/*.js"
            concat:
                # `raw_file_in` will be monitored for changes by `waf watch`
                raw_file_in: "{_1}/{_2}/js/**/*.js"
                # `{_1}:{_2}` will be replaced with the groups' names, in this
                # case it will be read as `djangoprj/blogapp/jshint`
                rule_in: "{_1}/{_2}/jshint"
                # Relative files are relative to the directory where you
                # run `waf configure`
                file_out: "js/blogapp.js"

        # Build group at level 2
        djangoprj:
            # Test javascript files syntax for errors
            jshint:
                options:
                    # Example of macro usage, see yaml node anchor.
                    # `_source_excluded_` is a special directive, excludes some
                    # files listed in `file_in` (could be from wildcards) from
                    # being processed.
                    _source_excluded_: *JSHINT_EXCLUDES
                file_in: "{_1}/{_2}/js/**/*.js"
            # Test javascript files syntax for errors
            jscs:
                options:
                    _source_excluded_: *JSHINT_EXCLUDES
                    # This one is defined here, not in higher level group
                    config_file: "etc/jscs.rc"
                file_in: "{_1}/{_2}/js/**/*.js"
            # Test python files syntax for errors
            pylint:
                raw_file_in: "{_1}/{_2}/**/*.py"
            # Concacenate javascript files into one file for production site
            concat:
                rule_in:
                    # Can has multiple items
                    -   "djangoprj/djangoprj/jshint"
                    -   "{_1}/{_2}/jscs"
                # The `@` symbol means to use the files produced by other tools
                file_in: "@{_1}/blogapp/concat"
                raw_file_in: "{_1}/{_2}/js/**/*.js"
                file_out: "js/djangoprj.js"
            # Copy final javascript file to production directory
            cp:
                file_in: "@{_1}/{_2}/concat"
                # Files usually produced in sandbox directories, `raw_file_out`
                # directive made it produced in the real project directory
                raw_file_out: "dist/"
            # Copy compressed final javascript file to production
            # directory
            uglifyjs:
                file_in: "@{_1}/{_2}/concat"
                # Directory as target is a okay, directory must ends with `/`.
                raw_file_out: "dist/"


Several things to keep in mind:

-   "djangoprj", "blogapp", "jshint", "concat" are group names.

-   JSHINT_EXCLUDES is not a group name (it matches all capital letters and
    underscore), pybuildtool will not recognize this entry, but ``yaml.load``
    will.
    It can be used as `yaml node anchor`_.

-   ``{_1}`` is string replacement thingy for a group name based on its level.

-   Because group name can be used as string replacement for file
    names, they can be used to represent directory structures.

-   "@djangoprj/djangoprj/jshint" is a reference to files
    generated by the rule "djangoprj"-"djangoprj"-"jshint", that is,
    the combination of its ``file_out``, ``raw_file_out`` and ``extra_out``.

-   You can use `ant glob`_ like this ``**/*.js``

-   You can use directory as output, they must end with path separator, for
    example: "minified_js/"

-   The child-most groups are special, they must match tool name like "jshint",
    "concat", "pylint", "uglifyjs", etc.

-   Rules are read in the order they are written, you can reference other rules
    generated output files as a input files but those rules must have been
    specified before.
    We don't support lazy loading of rules yet.

-   The directive ``raw_file_in`` or ``raw_depend_in`` is used for ``waf watch``
    to get list of files need to be monitored.

-   The directive ``depend_in`` can be used to force the tool to process
    ``file_in`` if files in ``depend_in`` changes.

-   The directive ``extra_out`` can be used to list auxiliary files produced by
    the tool, it can be used with combination of ``@group:group`` directive as
    inputs for other tools.

-   The option field: ``_source_excluded_`` is list of files which will be
    excluded from inputs.

-   The directive ``raw_file_out`` means this rule's outputs will be
    written in the actual file system, by default it's generated inside
    '.BUILD/stage/' directory.

-   The option field: ``config_file`` is configuration item provided by each
    tools, in this case it was provided by "pylint", "jshint", and "jscs", and
    they happened to have used the same name.  
    When option field is placed in higher group level, it's prefixed with the
    tool name, for example: "jscs_config_file"


Warning
-------

``waf`` does not like it if the source and target existed in the same directory,
see: `Files are always built`_.

If you used `rule_in` you may need to run `waf build` multiple times until there
was nothing to build, when the system is first initialize with `waf configure`
or by `waf clean`.

Install
-------

1.   ``pip install pybuildtool``


#.   Install **waf** as executable binary, download from `Waf project
     <http://waf.io>`_.

     You could also ``pip install waftools`` and then run ``wafinstall``,
     caution: this method will modify your ``~/.bashrc`` adding ``WAFDIR=???``.

#.   Copy and modify ``wscript`` in your project's root directory, specify the
     build tools your are going to use.

#.   Create ``build.yml`` with content like our example, this will be
     your build rules.

#.   ``waf configure``

#.   ``waf build_dev`` or ``waf watch_dev``


.. _ant glob: http://ant.apache.org/manual/dirtasks.html
.. _yaml node anchor: http://yaml.org/spec/1.2/spec.html#id2785586
.. _Files are always built: https://code.google.com/p/waf/wiki/FAQ#The_same_files_are_always_built
