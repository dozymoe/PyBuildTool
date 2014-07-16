"""
Patch apply changes to a file

Options:

    * patch-file : str, None, location of patch file (can be made using this
                   command `diff -Naur original_file current_file` > patch_file

Requirements:

    * patch

"""

from PyBuildTool.utils.common import (
    perform_shadow_jutsu,
    finalize_shadow_jutsu,
    silent_str_function,
)
from PyBuildTool.utils.warnings import InvalidOptions, ThereCanBeOnlyOne
from SCons.Action import Action
from SCons.Builder import Builder
from SCons.Node.Python import Value
from SCons.Errors import StopError


tool_name = 'patch'
file_processor = 'patch'


def tool_str(target, source, env):
    perform_shadow_jutsu(target=target, source=source, env=env)
    return env.subst('%s applied to $TARGETS.attributes.ItemName' % tool_name,
                     target=target)

def tool_generator(source, target, env, for_signature):
    perform_shadow_jutsu(target=target, source=source, env=env)

    src = [s.attributes.RealName for s in source if s.attributes.RealName]
    tgt = [t.attributes.RealName for t in target if t.attributes.RealName]

    if len(src) != 1:
        raise StopError(ThereCanBeOnlyOne, 
                        '%s only build one source' % tool_name)
    if len(tgt) != 1:
        raise StopError(ThereCanBeOnlyOne,
                        '%s only build one target' % tool_name)

    env['%s_BIN' % tool_name.upper()] = file_processor

    args = []
    cfg = env.get('TOOLCFG', {})
    if isinstance(cfg, Value): cfg = cfg.read()

    if cfg.get('patch-file') is None:
        raise StopError(InvalidOptions, '"patch-file" is missing')
    args.append('-i ' + cfg['patch-file'])

    env['%s_ARGS' % tool_name.upper()] = ' '.join(args)

    return [
        Action(finalize_shadow_jutsu, silent_str_function),
        Action(
            '${t}_BIN ${t}_ARGS -o $TARGETS.attributes.RealName '
            '$SOURCES.attributes.RealName'.format(t=tool_name.upper()),
             tool_str,
        ),
    ]


def generate(env):
    """ Add builders and construction variables to the Environment. """

    env['BUILDERS'][tool_name] = Builder(generator=tool_generator)


def exists(env):
    return env.Detect(file_processor)
