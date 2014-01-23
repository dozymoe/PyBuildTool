"""
Validate javascript files.

Options:

    * config-file      : str, None, jshint configuration file
    * reporter         : str, None, custom reporter
    * ignore-files     : list, [],  excludes files matching pattern
    * ignore-list-file : str, None, jshintignore file
"""

from PyBuildTool.utils.common import update_shadow_jutsu
from SCons.Action import Action
from SCons.Builder import Builder
from SCons.Defaults import Copy


tool_name = 'jslint'
file_processor = 'jshint'


def tool_str(target, source, env):
    return env.subst('%s passed $TARGETS' % file_processor,
                     target=target)


def tool_generator(source, target, env, for_signature):
    update_shadow_jutsu(target=target, source=source, env=env)
 
    env['%s_BIN' % tool_name.upper()] = file_processor

    args = []
    cfg = env['TOOLCFG'].read()

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

    cp = Copy(str(target[0]), str(source[0]))
    cp.strfunction = None

    return [
        Action('${t}_BIN ${t}_ARGS $SOURCES'.format(t=tool_name.upper()),
               tool_str,
        ),
        cp
    ]


def generate(env):
    """ Add builders and construction variables to the Environment. """

    env['BUILDERS'][tool_name] = Builder(generator=tool_generator,
                                         src_suffix='.js',
                                         single_source=True)


def exists(env):
    return env.Detect(file_processor)
