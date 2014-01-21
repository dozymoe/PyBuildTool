from PyBuildTool.tools.warnings import ThereCanBeOnlyOne
from SCons.Builder import Builder
from SCons.Errors import StopError


def cssmin_generator(source, target, env, for_signature):
    if len(target) != 1:
        raise StopError(ThereCanBeOnlyOne, 'cssmin only support one target')

    env['CSSMIN_BIN'] = 'yuicompressor'

    return '$CSSMIN_BIN -o "$TARGET" $SOURCE'


def generate(env):
    """ Add builders and construction variables to the Environment. """

    env['BUILDERS']['cssmin'] = Builder(generator=cssmin_generator,
                                        src_suffix='.css', suffix='.css')


def exists(env):
    return env.Detect('yuicompressor')
