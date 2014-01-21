def generate(env):
    """ Add builders and construction variables to the Environment. """

    # Here we use the builtin tool 'CopyAs' provided by SCons.
    env['BUILDERS']['copy'] = env['BUILDERS']['CopyAs']


def exists(env):
    return True
