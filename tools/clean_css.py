"""
Clean-css is a fast and efficient Node.js library for minifying CSS files.

Options:

    * keep-line-breaks     : bool, False, keep line breaks
    * no-comments          : bool, False, remove all special comments,
                             i.e /*! comment */
    * first-special-comment: bool, False, remove all special comments,
                             but the first one
    * root-path            : str, None, a root path to which resolve absolute
                             @import rules and rebase relative URLs
    * skip-import          : bool, False, disable @import processing
    * skip-rebase          : bool, False, disable URLs rebasing
    * skip-advanced        : bool, False, disable advanced optimizations -
                             selector & property merging, reduction, etc
    * skip-aggressive-merging: bool, False, disable properties merging based
                               on their order
    * rounding-precision   : int, 2, rounding precision
    * compatibility        : str, None, [ie7, ie8], force compatibility mode
    * timeout              : int, 5, per connection timeout when fetching
                             remote @imports (in seconds)
    * debug                : shows debug information (minification time &
                             compression efficiency)

Requirements:

    * clean-css
      to install, edit package.json, run `npm install`
    * node.js

"""

from PyBuildTool.utils.common import (
    perform_shadow_jutsu,
    finalize_shadow_jutsu,
    silent_str_function,
)
#from PyBuildTool.utils.warnings import ThereCanBeOnlyOne
from SCons.Action import Action
from SCons.Builder import Builder
#from SCons.Errors import StopError
from SCons.Node.Python import Value

tool_name = 'clean_css'
file_processor = 'node_modules/clean-css/bin/cleancss'

def tool_str(target, source, env):
    perform_shadow_jutsu(target=target, source=source, env=env)
    return env.subst('%s minified $TARGETS.attributes.RealName' % tool_name,
                     target=target)

def tool_generator(source, target, env, for_signature):
    perform_shadow_jutsu(target=target, source=source, env=env)

    #if len(source) != 1:
    #    raise StopError(ThereCanBeOnlyOne,
    #                    '%s only take one source' % tool_name)
    #if len(target) != 1:
    #    raise StopError(ThereCanBeOnlyOne,
    #                    '%s only build one target' % tool_name)

    env['%s_BIN' % tool_name.upper()] = file_processor

    args = []
    cfg = env.get('TOOLCFG', {})
    if isinstance(cfg, Value):  cfg = cfg.read()

    # keep line breaks
    if cfg.get('keep-line-breaks', False):
        args.append('--keep-line-breaks')

    # remove all special comments, i.e /*! comment */
    if cfg.get('no-comments', False):
        args.append('--s0')

    # remove all special comments but the first one
    if cfg.get('first-special-comment', False):
        args.append('--s1')

    # a root path to which resolve absolute @import rules and reabse relative
    # URLs
    if cfg.get('root-path', None):
        args.append('--root=%s' % cfg['root-path'])

    # disable @import processing
    if cfg.get('skip-import', False):
        args.append('--skip-import')

    # disable URLs rebasing
    if cfg.get('skip-rebase', False):
        args.append('--skip-rebase')

    # disable advanced optimizations - selector & property merging,
    # reduction, etc
    if cfg.get('skip-advanced', False):
        args.append('--skip-advanced')

    # disable properties merging based on their order
    if cfg.get('skip-aggressive-merging', False):
        args.append('--skip-aggressive-merging')

    # rounding precision
    if cfg.get('rounding-precision', None):
        args.append('--rounding-precision=%s' % cfg['rounding-precision'])

    # force compatibility mode
    if cfg.get('compatibility', None):
        args.append('--compatibility=%s' % cfg['compatibility'])

    # per connection timeout when fetching remote @improts (in seconds)
    if cfg.get('timeout', None):
        args.append('--timeout=%s' % cfg['timeout'])

    # show debug information (minification time & compression efficiency)
    if cfg.get('debug', False):
        args.append('--debug')

    env['%s_ARGS' % tool_name.upper()] = ' '.join(args)

    return [
        Action(finalize_shadow_jutsu, silent_str_function),
        Action(
            '${t}_BIN ${t}_ARGS $SOURCES.attributes.RealName '
            '-o $TARGETS.attributes.RealName'.format(t=tool_name.upper()),
            tool_str,
        ),
    ]

def generate(env):
    """Add builders and construction variables to the Environment."""

    env['BUILDERS'][tool_name] = Builder(generator=tool_generator)

def exists(env):
    return env.Detect(file_processor)
