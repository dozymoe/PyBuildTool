from PyBuildTool.tools.warnings import ThereCanBeOnlyOne
from SCons.Builder import Builder
from SCons.Errors import StopError


def stylus_generator(source, target, env, for_signature):
    if len(target) != 1:
        raise StopError(ThereCanBeOnlyOne, 'stylus only support one target')

    env['STYLUS_BIN'] = 'stylus'

    return '$STYLUS_BIN < $SOURCE > $TARGET'


def generate(env):
    """ Add builders and construction variables to the Environment. """

    env['BUILDERS']['stylus'] = Builder(generator=stylus_generator,
                                        src_suffix='.styl', suffix='.css')


def exists(env):
    return env.Detect('stylus')
