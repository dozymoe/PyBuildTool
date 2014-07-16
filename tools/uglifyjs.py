"""
UglifyJS is a JavaScript compressor/minifier written in JavaScript. It also
contains tools that allow one to automate working with Javascript code.

Options:

    * source-map        : str, None, specify an output file where to generate
                          source map
    * source-map-root   : str, None, the path to the original source to be
                          included in the source map
    * source-map-url    : str, None, the path to the source map to be added
                          in //# sourceMappingURL. Defaults to the value
                          passed with --source-map
    * source-map-include-sources: bool, None, pass this flag if you want to
                                  include the content of source files in the
                                  source map as sourcesContent property
    * in-source-map     : str, None, input source map, useful if you're
                          compressing JS that was generated from some other
                          original code
    * screw-ie8         : bool, None, pass this flag if you don't care about
                          full compliance with Internet Explorer 6-8 quirks
                          (by default UglifyJS will try to be IE-proof)
    * expr              : bool, None, parse a single expression, rather than a
                          program (for parsing JSON)
    * prefix            : str, None, skip prefix for original filenames that
                          appear in source maps. For example --prefix 3 will
                          drop 3 directories from file names and ensure they
                          are relative paths. You can also specify --prefix
                          relative, which will make UglifyJS figure out itself
                          the relative paths between original sources, the source
                          map and the output file
    * beautify          : str, None, beautify output/specify output options
    * mangle            : str, None, mangle names/pass mangler options
    * reserved          : str, None, reserved names to exclude from mangling
    * compress          : str, None, enable compressor/pass compressor options.
                          Pass options like --compress hoist_vars=false,if_return=false.
                          Use --compress with no argument to use the default
                          compression options
    * define            : str, None, global definitions
    * enclose           : str, None, embed everything in a big function, with a
                          configurable parameter/argument list
    * comments          : str, None, preserve copyright comments in the output.
                          By default this works like Google Closure, keeping
                          JSDoc-style comments that contain "@license" or
                          "@preserve". You can optionally pass one of the following
                          arguments to this flag:
                          - "all" to keep all comments
                          - a valid JS regexp (needs to start with a slash) to
                          keep only comments that match.
                          Note that currently not *all* comments can be kept when
                          compression is on, because of dead code removal or
                          cascading statements into sequences
    * preamble          : str, None, preamble to prepend to the output. You can
                          use this to insert a comment, for example for licensing
                          information. This will not be parsed, but the source
                          map will adjust for its presence
    * stats             : bool, None, display operations run time on STDERR
    * acorn             : bool, None, use Acorn for parsing
    * spidermonkey      : bool, None, assume input files are SpiderMonkey AST
                          format (as JSON)
    * self              : bool, None, build itself (UglifyJS2) as a library
                          (implies --wrap=UglifyJS --export-all)
    * wrap              : str, None, embed everything in a big function, making
                          the "exports" and "global" variables available. You
                          need to pass an argument to this option to specify the
                          name that your model will take when included in, say,
                          a browser
    * export-all        : bool, None, only used when --wrap, this tells UglifyJS
                          to add code to automatically export all globals
    * lint              : bool, None, display some scope warnings
    * verbose           : bool, None, verbose
    * noerr             : bool, None, don't throw an error for unknown options
                          in --compress, --beautify, --mangle

Requirements:

    * uglify-js
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

tool_name = 'uglifyjs'
file_processor = 'node_modules/uglify-js/bin/uglifyjs'

def tool_str(target, source, env):
    perform_shadow_jutsu(target=target, source=source, env=env)
    return env.subst('%s minified $TARGETS.attributes.RealName' % tool_name,
                     target=target)

def tool_generator(source, target, env, for_signature):
    perform_shadow_jutsu(target=target, source=source, env=env)

    env['%s_BIN' % tool_name.upper()] = file_processor

    args = []
    cfg = env.get('TOOLCFG', {})
    if isinstance(cfg, Value):  cfg = cfg.read()

    if cfg.get('source-map', None):
        args.append("--source-map='%s'" % cfg['source-map'])

    if cfg.get('source-map-root', None):
        args.append("--source-map-root='%s'" % cfg['source-map-root'])

    if cfg.get('source-map-url', None):
        args.append("--source-map-url='%s'" % cfg['source-map-url'])

    if cfg.get('source-map-include-sources', None):
        args.append('--source-map-include-sources')

    if cfg.get('in-source-map', None):
        args.append("--in-source-map='%s'" % cfg['in-source-map'])

    if cfg.get('screw-ie8', None):
        args.append('--screw-ie8')

    if cfg.get('expr', None):
        args.append('--expr')

    if cfg.get('prefix', None):
        args.append("--prefix='%s'" % cfg['prefix'])

    if cfg.get('beautify', None):
        args.appendd("--beautify='%s'" % cfg['beautify'])

    if not cfg.get('mangle', None) is None:
        if len(cfg['mangle']):
            args.append("--mangle='%s'" % cfg['mangle'])
        else:
            args.append('--mangle')

    if cfg.get('reserved', None):
        args.append("--reserved='%s'" % cfg['reserved'])

    if not cfg.get('compress', None) is None:
        if len(cfg['compress']):
            args.append("--compress='%s'" % cfg['compress'])
        else:
            args.append('--compress')

    if cfg.get('define', None):
        args.append("--define='%s'" % cfg['define'])

    if cfg.get('enclose', None):
        args.append("--enclose='%s'" % cfg['enclose'])

    if not cfg.get('comments', None) is None:
        if len(cfg['comments']):
            args.append("--comments='%s'" % cfg['comments'])
        else:
            args.append('--comments')

    if cfg.get('preamble', None):
        args.append("--preamble='%s'" % cfg['preamble'])

    if cfg.get('stats', None):
        args.append('--stats')

    if cfg.get('acorn', None):
        args.append('--acorn')

    if cfg.get('spidermonkey', None):
        args.append('--spidermonkey')

    if cfg.get('self', None):
        args.append('--self')

    if cfg.get('wrap', None):
        args.append("--wrap='%s'" % cfg['wrap'])

    if cfg.get('export-all', None):
        args.append('--export-all')

    if cfg.get('lint', None):
        args.append('--lint')

    if cfg.get('verbose', None):
        args.append('--verbose')

    if cfg.get('noerr', None):
        args.append('--noerr')

    env['%s_ARGS' % tool_name.upper()] = ' '.join(args)

    return [
        Action(finalize_shadow_jutsu, silent_str_function),
        Action(
            '${t}_BIN ${t}_ARGS --output="$TARGETS.attributes.RealName" '
            '$SOURCES.attributes.RealName'.format(t=tool_name.upper()),
            tool_str,
        ),
    ]

def generate(env):
    """Add builders and construction variables to the Environment."""

    env['BUILDERS'][tool_name] = Builder(generator=tool_generator)

def exists(env):
    return env.Detect(file_processor)
