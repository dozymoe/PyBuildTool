"""
gzip compress files.

Requirements:

    * gzip

"""

from PyBuildTool.utils.common import (
    perform_shadow_jutsu,
    finalize_shadow_jutsu,
    silent_str_function,
)
from PyBuildTool.utils.warnings import ThereCanBeOnlyOne
from SCons.Action import Action
from SCons.Builder import Builder
from SCons.Errors import StopError
from SCons.Node.Python import Value

tool_name = 'gzip'
file_processor = 'gzip'

def tool_str(target, source, env):
    perform_shadow_jutsu(target=target, source=source, env=env)
    return env.subst('%s compressed $SOURCES.attributes.RealName' % tool_name,
                     source=source)

def tool_generator(source, target, env, for_signature):
    perform_shadow_jutsu(target=target, source=source, env=env)

    src = [s.attributes.RealName for s in source if s.attributes.RealName]

    env['%s_BIN' % tool_name.upper()] = file_processor

    args = ['--stdout', '--best']

    env['%s_ARGS' % tool_name.upper()] = ' '.join(args)

    actions = [Action(finalize_shadow_jutsu, silent_str_function)]
    for source_file in src:
        actions.append(Action(
            '${t}_BIN ${t}_ARGS {s} > {s}.gz'.format(
                s=source_file,
                t=tool_name.upper(),
            ),
            silent_str_function,
        ))
    #actions.append( Action(tool_str, silent_str_function))
    return actions

def generate(env):
    """Add builders and construction variables to the Environment."""

    env['BUILDERS'][tool_name] = Builder(generator=tool_generator)

def exists(env):
    return env.Detect(file_processor)
