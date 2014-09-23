"""
Precompile handlebars templates.

Requirements:

    * handlebars
      to install, edit package.json, run `npm install`
    * node.js

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


tool_name = 'handlebars'
file_processor = 'node_modules/handlebars/bin/handlebars'


def tool_str(target, source, env):
    perform_shadow_jutsu(target=target, source=source, env=env)
    return env.subst('%s compiled $TARGETS.attributes.ItemName' % tool_name,
                     target=target)


def tool_generator(source, target, env, for_signature):
    perform_shadow_jutsu(target=target, source=source, env=env)

    src = [s.attributes.RealName for s in source if s.attributes.RealName]
    tgt = [t.attributes.RealName for t in target if t.attributes.RealName]

    if len(src) != 1:
        raise StopError(ThereCanBeOnlyOne,
                        '%s only take one source' % tool_name)
    if len(tgt) != 1:
        raise StopError(ThereCanBeOnlyOne,
                        '%s only build one target' % tool_name)

    env['%s_BIN' % tool_name.upper()] = file_processor

    args = []
    cfg = env.get('TOOLCFG', {})
    if isinstance(cfg, Value): cfg = cfg.read()

    env['%s_ARGS' % tool_name.upper()] = ' '.join(args)

    return [
        Action(finalize_shadow_jutsu, silent_str_function),
        Action(
            '${t}_BIN ${t}_ARGS $SOURCES.attributes.RealName '
            '-f $TARGETS.attributes.RealName'.format(t=tool_name.upper()),
             tool_str,
        ),
    ]


def generate(env):
    """ Add builders and construction variables to the Environment. """

    env['BUILDERS'][tool_name] = Builder(generator=tool_generator)


def exists(env):
    return env.Detect(file_processor)
