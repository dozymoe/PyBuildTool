"""
Preprocess CSS files using [Stylus](http://learnboost.github.io/stylus/).

Options:

    * plugins-path  : list, [],    location of stylus plugins
    * inline-image  : bool, False, use data URI
    * includes-path : list, [],    lookup paths
    * compress      : bool, False, compress CSS output
    * firebug       : bool, False, debug information for FireStylus
    * line-numbers  : bool, False, print out stylus line number
    * import-files  : bool, [],    always import selected stylus files
    * include-css   : bool, True,  pull in CSS files with @import
    * resolve-url   : bool, True,  resolve relative urls inside imports
"""

from PyBuildTool.tools.warnings import ThereCanBeOnlyOne
from SCons.Action import Action
from SCons.Builder import Builder
from SCons.Node.Python import Value
from SCons.Errors import StopError


tool_name = 'stylus'
file_processor = 'stylus'


def tool_str(target, source, env):
    return env.subst('CSS preprocessed $TARGET', target=target)


def tool_generator(source, target, env, for_signature):
    if len(source) != 1:
        raise StopError(ThereCanBeOnlyOne, 
                        '%s only build one source' % tool_name)
    if len(target) != 1:
        raise StopError(ThereCanBeOnlyOne,
                        '%s only build one target' % tool_name)

    env['%s_BIN' % tool_name.upper()] = file_processor

    args = []
    cfg = env.get('TOOLCFG', {})
    if isinstance(cfg, Value): cfg = cfg.read()

    # Utilize the Stylus plugin at <path>.
    plugin_dirs = cfg.get('plugins-path', [])
    if not isinstance(plugin_dirs, list):
        plugin_dirs = [plugin_dirs]
    for plugin_dir in plugin_dirs:
        args.append('--use=%s' % plugin_dir)

    # Utilize image inlining via data URI support.
    if cfg.get('inline-image', False):
        args.append('--inline')

    # Add <path> to lookup paths.
    include_dirs = cfg.get('includes-path', [])
    if not isinstance(include_dirs, list):
        include_dirs = [include_dirs]
    for include_dir in include_dirs:
        args.append('--include=%s' % include_dir)

    # Compress CSS output.
    if cfg.get('compress', False):
        args.append('--compress')

    # Emits debug infos in the generated CSS that can be used by the
    # FireStylus Firebug plugin.
    if cfg.get('firebug', False):
        args.append('--firebug')

    # Emits comments in the generated CSS indicating the corresponding
    # Stylus line
    if cfg.get('line-numbers', False):
        args.append('--line-numbers')

    # Import stylus <file>.
    import_files = cfg.get('import-files', [])
    if not isinstance(import_files, list):
        import_files = [import_files]
    for import_file in import_files:
        args.append('--import=%s' % import_file)

    # Include regular CSS on @import
    if cfg.get('include-css', True):
        args.append('--include-css')

    # Resolve relative urls inside imports
    if cfg.get('resolve-url', True):
        args.append('--resolve-url')

    env['%s_ARGS' % tool_name.upper()] = ' '.join(args)
    return Action('${t}_BIN ${t}_ARGS < $SOURCE > $TARGET'.format(t=tool_name.upper()),
                  tool_str)


def generate(env):
    """ Add builders and construction variables to the Environment. """

    env['BUILDERS'][tool_name] = Builder(generator=tool_generator,
                                        src_suffix='.styl', suffix='.css')


def exists(env):
    return env.Detect(file_processor)
