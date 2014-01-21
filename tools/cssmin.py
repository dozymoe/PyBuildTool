"""
Minify css using yuicompressor (a java application).

Options:

    * charset    : str, None, charset of the source file
    * line-width : int, None, maximum characters per line
"""

from PyBuildTool.tools.warnings import ThereCanBeOnlyOne
from SCons.Action import Action
from SCons.Builder import Builder
from SCons.Errors import StopError
from SCons.Node.Python import Value


tool_name = 'cssmin'
file_processor = 'yuicompressor'


def tool_str(target, source, env):
    return env.subst('CSS minified $TARGETS', target=target)

def tool_generator(source, target, env, for_signature):
    if len(source) != 1:
        raise StopError(ThereCanBeOnlyOne,
                        '%s only take one source' % tool_name)
    if len(target) != 1:
        raise StopError(ThereCanBeOnlyOne,
                        '%s only build one target' % tool_name)

    env['%s_BIN' % tool_name.upper()] = file_processor

    args = []
    cfg = env.get('TOOLCFG', {})
    if isinstance(cfg, Value): cfg = cfg.read()

    # Read the input file using <charset>
    if cfg.get('charset', None):
        args.append('--charset=%s' % cfg['charset'])

    # Insert a line break after the specified column number
    if cfg.get('line-width', None):
        args.append('--line-break=%s' % cfg['line-width'])

    env['%s_ARGS' % tool_name.upper()] = ' '.join(args)

    return Action('${t}_BIN ${t}_ARGS -o $TARGET $SOURCE'.format(t=tool_name.upper()),
                  tool_str)


def generate(env):
    """ Add builders and construction variables to the Environment. """

    env['BUILDERS'][tool_name] = Builder(generator=tool_generator,
                                         src_suffix='.css', suffix='.css')


def exists(env):
    return env.Detect(file_processor)
