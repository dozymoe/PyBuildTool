""" Copy files. """


tool_name = 'copy'


def generate(env):
    """ Add builders and construction variables to the Environment. """

    # Here we use the builtin tool 'CopyAs' provided by SCons.
    env['BUILDERS'][tool_name] = env['BUILDERS']['CopyAs']


def exists(env):
    return True
