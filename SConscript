from os import environ, getcwd, path
from PyBuildTool.utils.common import get_config_filename, read_config


Import('env ROOT_DIR BUILD_DIR')


# support different build stages (development, production, etc.).
AddOption('--stage', dest='stage', type='string',
          action='store', default='default',
          help='Build workflow stages, for example development' \
               ' or production')
env['ENV']['STAGE'] = GetOption('stage')


# support different type of configuration files (py and yml).
AddOption('--filetype', dest='filetype', 
          action='store', default='auto', choices=['auto', 'py', 'yml'],
          help='File type or file extension of main configuration file,'\
               ' for example SConsfile.yml with yml as the value.')

# support watch command.
AddOption('--watch', dest='watch', action='store_true', default=False,
          help='Watch file changes and automatically invoke scons build' \
               ' per group.')

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


# if `watch` argument specified, exit stage left.
if GetOption('watch'):
    from PyBuildTool.utils.watch import Watch

    watch = Watch(env=env, root_dir=ROOT_DIR,
                  stage=env['ENV']['STAGE'],
                  filetype=GetOption('filetype'))
    watch.run()
    exit(0)


# read build-configuration (files to process).
config_file = get_config_filename(root=ROOT_DIR,
                                  stage=env['ENV']['STAGE'],
                                  filetype=GetOption('filetype'))
config = read_config(basefilename=config_file[0],
                     filetype=config_file[1],
                     env=env, root_dir=ROOT_DIR)
                                  
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

            item['src'] = [path.join(prefix, src)
                           for src in item['src']]

            action = tool(item['dest'], item['src'],
                          TOOLCFG=Value(group_options))
            group_actions.append(action)
            tool_actions.append(action)

        env.Alias(group_alias, group_actions)
        if 'depends' in group:
            env.Depends(group_alias,
                        [Alias(depend) for depend in group_dependencies])
    env.Alias(tool_name, tool_actions)
