from fileinput import input
from PyBuildTool.tools.warnings import ThereCanBeOnlyOne
from SCons.Action import Action
from SCons.Builder import Builder
from SCons.Errors import StopError


def concat_func(target, source, env):
    if len(target) != 1:
        raise StopError(ThereCanBeOnlyOne, 'concat only supports one target')

    with open(str(target[0]), 'w') as fout:
        for line in input(str(f) for f in source):
            fout.write(line)
                
def concat_str(target, source, env):
    return env.subst('Merge file(s): "$SOURCES" into "$TARGETS"',
                     source=source, target=target)


def generate(env):
    """ Add builders and construction variables to the Environment. """

    env['BUILDERS']['concat'] = Builder(action=Action(concat_func, concat_str))


def exists(env):
    return True
