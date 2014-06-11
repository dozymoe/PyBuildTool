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

    src = [s.attributes.RealName for s in source if s.attributes.RealName]
    tgt = [t.attributes.RealName for t in target if t.attributes.RealName]

    for dest in tgt:
        # `copy_func()` requires that the target directory exists
        # before copying, odd.
        if dest.endswith(sep):
            dest_dir = dest
        else:
            dest_dir = path.dirname(dest)
        if not path.exists(dest_dir):
            makedirs(dest_dir)

        for s in src:  copy_func(dest, s)


def tool_str(target, source, env):
    perform_shadow_jutsu(target, source, env)
    return env.subst('Copied file $TARGETS.attributes.ItemName', target=target)


def generate(env):
    """ Add builders and construction variables to the Environment. """

    env['BUILDERS'][tool_name] = Builder(
        action=Action(tool_func, strfunction=tool_str)
    )


def exists(env):
    return True
