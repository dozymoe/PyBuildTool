from copy import deepcopy
from os import environ, getcwd, path


def get_config_filename(root, stage, filetype):
    """ oh my, there are several possibilities for our main
        configuration filename. """

    possible_types = ('py', 'yml') if filetype == 'auto' \
                     else (filetype,)
    possible_stage = ('.default', '') if stage == 'default' \
                     else ('.%s' % stage,)
    possible_confs = (('SConsfile%s' % p_stage, p_type) \
                      for p_stage in possible_stage \
                      for p_type in possible_types)

    for p_conf in possible_confs:
        if path.lexists(path.join(root, '.'.join(p_conf))):
            return p_conf

    raise Exception('Missing configuration file (SConsfile.STAGE.EXT)')




Import('env ROOT_DIR BUILD_DIR')


# support different build stages (development, production, etc.).
AddOption('--stage', dest='stage', type='string',
          action='store', default='default',
          help='Build workflow stages, for example development' \
               ' or production')
env['ENV']['STAGE'] = GetOption('stage')


# support different type of configuration files (py and yml).
AddOption('--config-filetype', dest='filetype', type='string',
          action='store', default='auto',
          help='File type or file extension of main configuration file,'\
               ' for example SConsfile.yml with yml as the value.')


# populate scons' shell-environment-variable $PATH with system's $PATH.
for p in environ['PATH'].split(':'):
    env.AppendENVPath('PATH', p)


# tell SCons where to find our tools.
toolpath = env.get('toolpath', [])
toolpath.append(path.join(getcwd(), 'tools'))
env['toolpath'] = toolpath


# setup sandbox for temporary build files.
prefix = path.join(BUILD_DIR, env['ENV']['STAGE'])
env.VariantDir(prefix, ROOT_DIR)


# read build-configuration (files to process).
config_file = get_config_filename(root=ROOT_DIR,
                                  stage=env['ENV']['STAGE'],
                                  filetype=GetOption('filetype'))
if config_file[1] == 'py':
    # our config dictionary would be the module level variable `build_config`
    # inside SConsfile.STAGE.py

    from  importlib import import_module
    myconfig = import_module(config_file[0])

    initfunc = getattr(myconfig, 'init', None)
    if initfunc is not None:
        initfunc(env)
    mybuildconfig = getattr(myconfig, 'build_config')
    
    config = deepcopy(mybuildconfig)
elif config_file[1] == 'yml':
    # our config dictionary would be the whole contents of SConsfile.STAGE.yml
    
    from yaml import safe_load as yaml_load
    config = yaml_load(open(path.join(ROOT_DIR, '.'.join(config_file))))
                                  

# main function, process build config into tasks.
for tool_name in config:
    env.Tool(tool_name)

    tool = getattr(env, tool_name)
    tool_actions = []

    for group_name in config[tool_name]:
        group = config[tool_name][group_name]

        group_actions = []
        group_alias = '%s:%s' % (tool_name, group_name)
        group_dependencies = group.get('depends', [])
        group_options = group.get('options', {})

        for item in group['files']:
            # reconstruct files into list
            if not isinstance(item['dest'], list):
                item['dest'] = [item['dest']]
            if not isinstance(item['src'], list):
                item['src'] = [item['src']]

            # files are either relative to build dir, or relative
            # to ROOT_DIR.
            # ROOT_DIR is where SConsfile.yml lies.
            if group_options.get('_target_sandboxed_', True):
                item['dest'] = [path.join(prefix, dest)
                                for dest in item['dest']]
            else:
                item['dest'] = [path.join(ROOT_DIR, dest)
                                for dest in item['dest']]

            action = tool(item['dest'], item['src'],
                          TOOLCFG=Value(group_options))
            group_actions.append(action)
            tool_actions.append(action)

        env.Alias(group_alias, group_actions)
        if 'depends' in group:
            env.Depends(group_alias,
                        [Alias(depend) for depend in group_dependencies])
    env.Alias(tool_name, tool_actions)
