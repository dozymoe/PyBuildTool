""" Merge files from sources into copious targets. """

from PyBuildTool.utils.common import update_shadow_jutsu
from SCons.Action import Action
from SCons.Builder import Builder


tool_name = 'concat'


def tool_func(target, source, env):
    update_shadow_jutsu(target=target, source=source, env=env)

    for dest in target:
        with open(dest.attributes.ActualName, 'w') as fout:
            for src in source:
                with open(src.attributes.ActualName) as fin:
                    for line in fin:
                        fout.write(line)
                

def tool_str(target, source, env):
    return env.subst('Merged file $TARGETS',
                     target=target)


def generate(env):
    """ Add builders and construction variables to the Environment. """

    env['BUILDERS'][tool_name] = Builder(action=Action(tool_func, tool_str))


def exists(env):
    return True
