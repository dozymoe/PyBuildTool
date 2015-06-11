# where `waf` will store its configuration
top = '.'
# directory for temporary files created during build process
out = '.BUILD'

# Constants

# stages, for example: 'dev' will provide separate build environment with
# commands like `waf build_dev` and `waf clean_dev`, that is build variants
STAGES = ('dev', 'stage', 'prod')


def build(bld):
    # load main configuration file
    import os, yaml
    from helper import prepare_targets, OrderedDictYAMLLoader
    conf_file = os.path.join(bld.path.abspath(), 'build_rules.yml')
    with open(conf_file) as f:
        conf = yaml.load(f, Loader=OrderedDictYAMLLoader)
    # parse data as waf tasks
    prepare_targets(conf, bld)


def options(opt):
    # add loadable modules from waf root directory
    import sys
    sys.path.append(opt.path.abspath())
    # load predefined tools from pybuildtool
    from imp import find_module
    pybuildtool_dir = find_module('pybuildtool')[1]
    opt.load('watch', tooldir=pybuildtool_dir)


def configure(ctx):
    # load predefined tools from pybuildtool
    from imp import find_module
    pybuildtool_dir = find_module('pybuildtool')[1]
    #ctx.load('autoprefixer', tooldir=pybuildtool_dir)
    #ctx.load('browserify', tooldir=pybuildtool_dir)
    #ctx.load('cleancss', tooldir=pybuildtool_dir)
    #ctx.load('concat', tooldir=pybuildtool_dir)
    #ctx.load('cp', tooldir=pybuildtool_dir)
    #ctx.load('gzip', tooldir=pybuildtool_dir)
    #ctx.load('handlebars', tooldir=pybuildtool_dir)
    #ctx.load('jinja', tooldir=pybuildtool_dir)
    #ctx.load('jshint', tooldir=pybuildtool_dir)
    #ctx.load('lesscss', tooldir=pybuildtool_dir)
    #ctx.load('lftp', tooldir=pybuildtool_dir)
    #ctx.load('nunjucks', tooldir=pybuildtool_dir)
    #ctx.load('patch', tooldir=pybuildtool_dir)
    #ctx.load('pngcrush', tooldir=pybuildtool_dir)
    #ctx.load('pylint', tooldir=pybuildtool_dir)
    #ctx.load('rjs', tooldir=pybuildtool_dir)
    #ctx.load('scp', tooldir=pybuildtool_dir)
    #ctx.load('shell', tooldir=pybuildtool_dir)
    #ctx.load('stylus', tooldir=pybuildtool_dir)
    #ctx.load('ttf2eot', tooldir=pybuildtool_dir)
    #ctx.load('ttf2svg', tooldir=pybuildtool_dir)
    #ctx.load('ttf2woff', tooldir=pybuildtool_dir)
    #ctx.load('uglifyjs', tooldir=pybuildtool_dir)


from waflib.Build import BuildContext, CleanContext, InstallContext
from waflib.Build import UninstallContext
from waflib.Context import Context

class WatchContext(Context):
    cmd = 'watch'
    fun = 'watch'
    variant = STAGES[0]

for stage in STAGES:
    for build_class in (BuildContext, CleanContext, InstallContext,
            UninstallContext, WatchContext):
        name = build_class.__name__.replace('Context', '').lower()
        class TempClass(build_class):
            cmd = name + '_' + stage
            variant = stage
