"""
Validate python files.

Requirements:

    * pylint (python library)

Options:

    * work-dir         : str,      None,  change current directory before
                                          running pylint
    * error-only       : bool,     None,  only check for errors
    * config-file      : str,      None,  pylint configuration file
    * plugins          : list:str, [] ,   plugins to load (ex. pylint_django)
    * reporter         : str,      None,  custom reporter
    * full-report      : bool,     False, full report or only the messages
"""

import os
from PyBuildTool.utils.common import (
    perform_shadow_jutsu,
    finalize_shadow_jutsu,
    silent_str_function,
)
from SCons.Action import Action
from SCons.Builder import Builder


tool_name = 'pylint'
file_processor = 'pylint'


def tool_str(target, source, env):
    perform_shadow_jutsu(target=target, source=source, env=env)
    return env.subst('%s passed $SOURCES.attributes.RealName' % tool_name,
                     source=source,target=target)


def tool_generator(source, target, env, for_signature):
    perform_shadow_jutsu(target=target, source=source, env=env)
 
    env['%s_BIN' % tool_name.upper()] = file_processor

    args = []
    cfg = env['TOOLCFG'].read()

    # Change current directory, before running pylint, helps module imports
    if cfg.get('work-dir', None):
        env['WORK_DIR'] = cfg['work-dir']

    # Specify a configuration file
    if cfg.get('config-file', None):
        args.append('--rcfile=' + os.path.join(env['ROOT_DIR'],
                                               cfg['config-file']))

    # Set the output format. Available formats are text,
    # parseable, colorized, msvs (visual studio) and html.
    # You can also give a reporter class, eg
    # mypackage.mymodule.MyReporterClass. [current: text]
    if cfg.get('reporter', None):
        args.append('--output-format=%s' % cfg['reporter'])

    # In error mode, checkers without error messages are
    # disabled and for others, only the ERROR messages are
    # displayed, and no reports are done by default
    if cfg.get('error-only', None):
        args.append('--errors-only')

    # Tells whether to display a full report or only the
    # messages [current: yes]
    if cfg.get('full-report', False):
        args.append('--reports=y')
    else:
        args.append('--reports=n')

    # Plugins
    plugins = cfg.get('plugins', [])
    if not isinstance(plugins, list):
        plugins = [plugins]
    if plugins:
        args.append('--load-plugins=%s' % ','.join(plugins))

    env['%s_ARGS' % tool_name.upper()] = ' '.join(args)

    return [
        Action(finalize_shadow_jutsu, silent_str_function),
        Action(
            'cd $WORK_DIR; ${t}_BIN ${t}_ARGS '
            '$SOURCES.attributes.RealName'.format(t=tool_name.upper()),
            tool_str,
        ),
    ]


def generate(env):
    """ Add builders and construction variables to the Environment. """

    env['BUILDERS'][tool_name] = Builder(generator=tool_generator)


def exists(env):
    return env.Detect(file_processor)
