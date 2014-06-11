""" Merge files from sources into copious targets. """

from PyBuildTool.utils.common import (perform_shadow_jutsu,
                                      finalize_shadow_jutsu)
from SCons.Action import Action
from SCons.Builder import Builder


tool_name = 'concat'


def tool_func(target, source, env):
    perform_shadow_jutsu(target, source, env)
    finalize_shadow_jutsu(target, source, env=env)

    srcs = (s.attributes.RealName for s in source if s.attributes.RealName)
    tgts = (t.attributes.RealName for t in target if t.attributes.RealName)

    for dest in tgts:
        with open(dest, 'w') as fout:
            for src in srcs:
                with open(src) as fin:
                    for line in fin:
                        fout.write(line)
                

def tool_str(target, source, env):
    perform_shadow_jutsu(target, source, env)
    return env.subst('Merged file $TARGETS.attributes.RealName',
                     target=target)


def generate(env):
    """ Add builders and construction variables to the Environment. """

    env['BUILDERS'][tool_name] = Builder(action=Action(tool_func, tool_str))


def exists(env):
    return True
