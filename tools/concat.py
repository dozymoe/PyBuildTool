""" Merge files from sources into copious targets. """

from SCons.Action import Action
from SCons.Builder import Builder


tool_name = 'concat'


def tool_func(target, source, env):
    for dest in target:
        with open(str(dest), 'w') as fout:
            for src in source:
                with open(str(src)) as fin:
                    for line in fin:
                        fout.write(line)
                
def tool_str(target, source, env):
    return env.subst('Merged file $TARGETS', target=target)


def generate(env):
    """ Add builders and construction variables to the Environment. """

    env['BUILDERS'][tool_name] = Builder(action=Action(tool_func, tool_str))


def exists(env):
    return True
