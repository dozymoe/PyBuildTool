from PyBuildTool.tools.warnings import ThereCanBeOnlyOne
from SCons.Builder import Builder
from SCons.Errors import StopError


def jsmin_generator(source, target, env, for_signature):
    if len(target) != 1:
        raise StopError(ThereCanBeOnlyOne, 'jsmin only support one target')

    env['JSMIN_BIN'] = 'yuicompressor'

    return '$JSMIN_BIN -o "$TARGET" $SOURCE'


def generate(env):
    """ Add builders and construction variables to the Environment. """

    env['BUILDERS']['jsmin'] = Builder(generator=jsmin_generator,
                                        src_suffix='.js', suffix='.js')


def exists(env):
    return env.Detect('yuicompressor')
