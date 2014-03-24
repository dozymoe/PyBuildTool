""" Copy files. """

from os import makedirs, path, sep
from PyBuildTool.utils.common import (perform_shadow_jutsu,
                                      finalize_shadow_jutsu)
from SCons.Action import Action
from SCons.Defaults import copy_func
from SCons.Builder import Builder


tool_name = 'copy'


def tool_func(target, source, env):
    perform_shadow_jutsu(target, source, env)
    finalize_shadow_jutsu(target, source, env)

    if len(source) == 1:
        src = source[0].attributes.ActualName
    else:
        src = [s.attributes.ActualName for s in source]

    for t in target:
        dest = t.attributes.ActualName

        # `copy_func()` requires that the target directory exists
        # before copying, odd.
        if dest.endswith(sep) and not path.exists(dest):
            makedirs(dest)

        copy_func(dest, src)


def tool_str(target, source, env):
    perform_shadow_jutsu(target, source, env)
    return env.subst('Copied file $TARGETS.attributes.ActualName', target=target)


def generate(env):
    """ Add builders and construction variables to the Environment. """

    env['BUILDERS'][tool_name] = Builder(
        action=Action(tool_func, strfunction=tool_str)
    )


def exists(env):
    return True
