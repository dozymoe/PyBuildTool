""" Copy files. """

from os import makedirs, path
from SCons.Action import Action
from SCons.Defaults import copy_func
from SCons.Node.FS import Dir
from SCons.Builder import Builder


tool_name = 'copy'


def tool_func(target, source, env):
    if len(source) == 1:
        src = str(source[0])
    else:
        src = [str(s) for s in source]
    for dest in target:
        dest_str = str(dest)
        if isinstance(dest, Dir):
            if not path.exists(dest_str):
                makedirs(dest_str)
        copy_func(dest_str, src)


def tool_str(target, source, env):
    return env.subst('Copied file $TARGETS', target=target)


def generate(env):
    """ Add builders and construction variables to the Environment. """

    env['BUILDERS'][tool_name] = Builder(
        action=Action(tool_func, strfunction=tool_str)
    )


def exists(env):
    return True
