"""
Validate javascript files.

Options:

    * config-file      : str, None, jshint configuration file
    * reporter         : str, None, custom reporter
    * ignore-files     : list, [],  excludes files matching pattern
    * ignore-list-file : str, None, jshintignore file
"""

from PyBuildTool.tools.warnings import ThereCanBeOnlyOne
from SCons.Action import Action
from SCons.Builder import Builder
from SCons.Defaults import Copy
from SCons.Errors import StopError
from SCons.Node.Python import Value


tool_name = 'jslint'
file_processor = 'jshint'


def tool_str(target, source, env):
    return env.subst('JS-lint $TARGETS', target=target)


def tool_generator(source, target, env, for_signature):
    if len(source) != 1:
        raise StopError(ThereCanBeOnlyOne,
                        '%s only take one source' % tool_name)
    if len(target) != 1:
        raise StopError(ThereCanBeOnlyOne,
                        '%s only build one target' % tool_name)

    env['%s_BIN' % tool_name.upper()] = file_processor

    args = []
    cfg = env.get('TOOLCFG', {})
    if isinstance(cfg, Value): cfg = cfg.read()

    # Custom configuration file
    if cfg.get('config-file', None):
        args.append('--config=%s' % cfg['config-file'])

    # Custom reporter (<PATH>|jslint|checkstyle)
    if cfg.get('reporter', None):
        args.append('--reporter=%s' % cfg['reporter'])

    # Exclude files matching the given filename pattern
    # (same as .jshintignore)
    exclude_files = cfg.get('ignore-files', [])
    if not isinstance(exclude_files, list):
        exclude_files = [exclude_files]
    for exclude_file in exclude_files:
        args.append('--exclude=%s' % exclude_file)

    # Pass in custom jshintignore file path
    if cfg.get('ignore-list-file', None):
        args.append('--exclude-path=%s' % cfg['ignore-list-file'])


    env['%s_ARGS' % tool_name.upper()] = ' '.join(args)

    copy = Copy("$TARGET", "$SOURCE")
    copy.strfunction = None

    return [Action('${t}_BIN ${t}_ARGS $SOURCES'.format(t=tool_name.upper()),
                   tool_str),
            copy]


def generate(env):
    """ Add builders and construction variables to the Environment. """

    env['BUILDERS'][tool_name] = Builder(generator=tool_generator,
                                         src_suffix='.js', suffix='.js',
                                         single_source=True)


def exists(env):
    return env.Detect(file_processor)
